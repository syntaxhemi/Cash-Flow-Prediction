"""Dataset preprocessing, aggregation, and temporal-window construction."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from training.config import FeatureConfig


@dataclass(slots=True)
class PreparedData:
    temporal: pd.DataFrame
    static: pd.DataFrame


@dataclass(slots=True)
class SequenceData:
    sequences: np.ndarray
    static: np.ndarray
    labels: np.ndarray
    companies: np.ndarray
    label_months: np.ndarray


def _prepare_account_receivable(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.rename(columns={'paper_or_electronic': 'electronic'}).copy()
    result['electronic'] = result['electronic'] == 'e'
    result['invoice_date'] = pd.to_datetime(
        result['invoice_date'] + '/2021', format='%d/%m/%Y'
    )
    result['end_date'] = pd.to_datetime(result['end_date'] + '/2021', format='%d/%m/%Y')
    result['payment_delay'] = (result['end_date'] - result['invoice_date']).dt.days
    result['month'] = result['invoice_date'].dt.to_period('M')
    return result


def _prepare_businesses(frame: pd.DataFrame) -> pd.DataFrame:
    columns = [
        'company_reg_number',
        'annual_turnover',
        'capex',
        'cogs',
        'cogs_plus_capex',
        'accounts_receivable',
        'current_assets',
        'current_liabilities',
        'fixed_assets',
        'long_term_liabilities',
        'capital_and_reserves',
        'provisions_for_liabilities',
        'number_of_employees',
        'entity_status',
        'dissolved_on',
    ]
    result = frame[columns].copy()
    result['turnover_level'] = result['annual_turnover'].map(
        {'0-632k': 0, '632k-10.2M': 1}
    )
    result['employee_size_level'] = result['number_of_employees'].map(
        {'0-4 People': 0, '5-9 People': 1, '10-19 People': 2, '20-49 People': 3}
    )
    result = result.drop(columns=['annual_turnover', 'number_of_employees'])
    result['dissolved_on'] = pd.to_datetime(result['dissolved_on'], format='%d-%m-%Y')
    return result.dropna(subset=['capex'])


def _prepare_credit_account_history(frame: pd.DataFrame) -> pd.DataFrame:
    columns = [
        'company_reg_number',
        'number_of_accounts',
        'current_acc_fraction',
        'total_amount',
        'pay_in_amount',
        'pay_out_amount',
        'rev_ratio',
        'cost_ratio',
    ]
    return frame[columns].dropna(subset=['total_amount']).copy()


def _prepare_credit_card_history(frame: pd.DataFrame) -> pd.DataFrame:
    columns = [
        'company_reg_number',
        'cc_agreed_limit',
        'cc_balance_limit_ratio',
        'cc_missed_payments',
        'missed_payments_number',
    ]
    result = frame[columns].copy()
    result['cc_missed_payments'] = result['cc_missed_payments'].fillna(0)
    return result


def _prepare_credit_rating(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame[
        [
            'company_reg_number',
            'credit_report_total_indebtedness',
            'missed_and_late_payments_last_five_years',
            'payment_index',
            'business_failure_score',
            'credit_report_credit_score',
            'ratio_debt_to_revenue',
        ]
    ].copy()
    return result.rename(
        columns={
            'credit_report_total_indebtedness': 'total_debt',
            'missed_and_late_payments_last_five_years': 'missed_payments_5y',
            'business_failure_score': 'failure_score',
            'credit_report_credit_score': 'credit_score',
            'ratio_debt_to_revenue': 'debt_to_revenue_ratio',
        }
    )


def _prepare_loan(frame: pd.DataFrame) -> pd.DataFrame:
    result = (
        frame[
            [
                'company_reg_number',
                'loan_original_amount',
                'loan_amount_outstanding_including_future_interest',
                'loan_start_date',
                'loan_date_due_to_close',
                'loan_number_of_missed_payments',
                'loan_default_date',
                'interest',
            ]
        ]
        .rename(
            columns={
                'loan_original_amount': 'loan_amount',
                'loan_amount_outstanding_including_future_interest': (
                    'loan_outstanding_with_interest'
                ),
                'loan_date_due_to_close': 'loan_maturity_date',
                'loan_number_of_missed_payments': 'loan_missed_payments',
                'interest': 'loan_interest_rate',
            }
        )
        .copy()
    )
    result['loan_is_defaulted'] = result['loan_default_date'].notna().astype(int)
    result = result.drop(columns=['loan_default_date'])
    result['loan_interest_rate'] = result['loan_interest_rate'].fillna(
        result['loan_interest_rate'].median()
    )
    result['loan_start_date'] = pd.to_datetime(result['loan_start_date'])
    result['loan_maturity_date'] = pd.to_datetime(result['loan_maturity_date'])
    result['month'] = result['loan_start_date'].dt.to_period('M')
    duration = (result['loan_maturity_date'] - result['loan_start_date']).dt.days / 30
    result['monthly_repayment'] = result['loan_outstanding_with_interest'] / duration
    return result


def prepare_datasets(datasets: dict[str, pd.DataFrame]) -> PreparedData:
    accounts = _prepare_account_receivable(datasets['account_receivable'])
    businesses = _prepare_businesses(datasets['businesses'])
    credit_accounts = _prepare_credit_account_history(
        datasets['credit_account_history']
    )
    credit_cards = _prepare_credit_card_history(datasets['credit_card_history'])
    ratings = _prepare_credit_rating(datasets['credit_rating'])
    loans = _prepare_loan(datasets['loan'])

    monthly_invoices = (
        accounts.groupby(['company_reg_number', 'month'])
        .agg(
            total_invoice_amount=('invoice_amount', 'sum'),
            payment_delay=('payment_delay', 'sum'),
        )
        .reset_index()
    )
    credit_history = (
        credit_accounts.groupby('company_reg_number')
        .agg(
            pay_in_amount=('pay_in_amount', 'sum'),
            pay_out_amount=('pay_out_amount', 'sum'),
        )
        .reset_index()
    )
    loan_monthly = (
        loans.groupby(['company_reg_number', 'month'])
        .agg(
            monthly_repayment=('monthly_repayment', 'sum'),
        )
        .reset_index()
    )

    temporal = monthly_invoices.merge(credit_history, on='company_reg_number')
    temporal = temporal.merge(
        loan_monthly, on=['company_reg_number', 'month'], how='left'
    ).fillna(0)
    temporal['total_inflows'] = (
        temporal['total_invoice_amount'] + temporal['pay_in_amount']
    )
    temporal['total_outflows'] = (
        temporal['pay_out_amount'] + temporal['monthly_repayment']
    )
    zero_outflows = temporal['total_outflows'] == 0
    total_pay_in = credit_history['pay_in_amount'].sum()
    total_pay_out = credit_history['pay_out_amount'].sum()
    pay_ratio = total_pay_out / total_pay_in if total_pay_in else 0
    temporal.loc[zero_outflows, 'total_outflows'] = (
        temporal.loc[zero_outflows, 'total_inflows'] * pay_ratio
    )
    temporal['net_cash_flow'] = temporal['total_inflows'] - temporal['total_outflows']

    static = businesses.merge(ratings, on='company_reg_number', how='left')
    static = static.merge(credit_cards, on='company_reg_number', how='left')
    return PreparedData(temporal=temporal, static=static.fillna(0))


def build_sequences(
    temporal: pd.DataFrame,
    static: pd.DataFrame,
    config: FeatureConfig,
) -> SequenceData:
    frame = temporal.copy()
    frame['month'] = frame['month'].dt.to_timestamp()
    frame = frame.sort_values(['company_reg_number', 'month'])
    static_indexed = static.groupby('company_reg_number')[config.static_features].mean(
        numeric_only=True
    )

    sequences: list[np.ndarray] = []
    static_values: list[np.ndarray] = []
    labels: list[float] = []
    companies: list[object] = []
    label_months: list[pd.Timestamp] = []
    grouped = frame.groupby('company_reg_number', sort=False)

    for company, group in grouped:
        group = group.reset_index(drop=True)

        if len(group) < config.sequence_length + 1:
            continue

        for start in range(len(group) - config.sequence_length):
            end = start + config.sequence_length
            sequences.append(
                group.loc[start : end - 1, config.temporal_features].values
            )
            label_value = group.loc[end, config.label_column]
            labels.append(float(pd.to_numeric(label_value)))
            companies.append(company)
            label_months.append(pd.Timestamp(str(group.loc[end, 'month'])))

            if company in static_indexed.index:
                static_values.append(
                    np.asarray(static_indexed.loc[company].values, dtype=float)
                )
            else:
                static_values.append(np.zeros(len(config.static_features)))

    return SequenceData(
        sequences=np.asarray(sequences, dtype=float),
        static=np.asarray(static_values, dtype=float),
        labels=np.asarray(labels, dtype=float),
        companies=np.asarray(companies),
        label_months=np.asarray(label_months),
    )
