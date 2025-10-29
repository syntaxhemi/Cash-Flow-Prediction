import { useState } from "react";
import Input from "./Input";

const Prediction = () => {
    const [seqData, setSeqData] = useState({
        total_invoice_amount: 0.0,
        payment_delay: 0,
        monthly_repayment: 0.0,
        total_inflows: 0.0,
        total_outflows: 0.0,
    });

    const [staticData, setStaticData] = useState({
        capex: 0.0,
        cogs: 0.0,
        current_assets: 0.0,
        current_liabilities: 0.0,
        fixed_assets: 0.0,
        long_term_liabilities: 0.0,
        credit_score: 0.0,
        failure_score: 0.0,
        debt_to_revenue_ratio: 0.0,
        missed_payments_number: 0.0,
    });

    const [result, setResult] = useState(null);

    const [error, setError] = useState("");

    const convertStateToNumbers = (state) => {
        return Object.fromEntries(
            Object.entries(state).map(([key, value]) => {
                return [key, Number(value)];
            })
        );
    };

    const handleSubmit = async () => {
        const payload = {
            seq_input: convertStateToNumbers(seqData),
            static_input: convertStateToNumbers(staticData),
        };

        const response = await fetch(`${import.meta.env.VITE_API_URL}/infer`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            console.log(
                `Error while making request to API: ${response.statusText}`
            );
            setError(response.statusText);
        } else {
            const json = await response.json();
            setResult(json["net_cash_flow"]);
        }
    };

    return (
        <div className="flex flex-col gap-8 bg-gray-100 px-50 py-10">
            <div className="flex flex-col gap-10">
                <h2 className="text-xl text-blue-900">Business Information</h2>
                <div>
                    <section className="flex py-6 border-t border-gray-300">
                        <div className="w-1/3 flex flex-col gap-4">
                            <h4 className="text-blue-900">
                                Business Fundamentals
                            </h4>
                            <p className="text-sm text-gray-500">
                                These are key financial indicators, like assets
                                and credit scores, that show the company's
                                long-term stability and overall financial
                                health.
                            </p>
                        </div>
                        <div className="flex flex-1 px-14">
                            <div className="w-full grid grid-cols-2 gap-x-10 gap-y-5">
                                <Input
                                    data={staticData}
                                    setData={setStaticData}
                                    name="capex"
                                    label="Capex"
                                />
                                <Input
                                    data={staticData}
                                    setData={setStaticData}
                                    name="cogs"
                                    label="COGS"
                                />
                                <Input
                                    data={staticData}
                                    setData={setStaticData}
                                    name="current_assets"
                                    label="Current Assets"
                                />
                                <Input
                                    data={staticData}
                                    setData={setStaticData}
                                    name="current_liabilities"
                                    label="Current Liabilities"
                                />
                                <Input
                                    data={staticData}
                                    setData={setStaticData}
                                    name="fixed_assets"
                                    label="Fixed Assets"
                                />
                                <Input
                                    data={staticData}
                                    setData={setStaticData}
                                    name="long_term_liabilities"
                                    label="Long-Term Liabilities"
                                />
                                <Input
                                    data={staticData}
                                    setData={setStaticData}
                                    name="credit_score"
                                    label="Credit Score"
                                />
                                <Input
                                    data={staticData}
                                    setData={setStaticData}
                                    name="failure_score"
                                    label="Failure Score"
                                />
                                <Input
                                    data={staticData}
                                    setData={setStaticData}
                                    name="debt_to_revenue_ratio"
                                    label="Debt to Revenue Ratio"
                                />
                                <Input
                                    data={staticData}
                                    setData={setStaticData}
                                    name="missed_payments_number"
                                    label="Missed Payments"
                                />
                            </div>
                        </div>
                    </section>
                    <section className="flex py-6 border-t border-gray-300">
                        <div className="w-1/3 flex flex-col gap-4">
                            <h4 className="text-blue-900">Transaction Data</h4>
                            <p className="text-sm text-gray-500">
                                This is data from day-to-day operations, such as
                                payments, invoices, and cash flow.
                            </p>
                        </div>
                        <div className="flex flex-1 px-14">
                            <div className="w-full grid grid-cols-2 gap-x-10 gap-y-5">
                                <Input
                                    data={seqData}
                                    setData={setSeqData}
                                    name="total_invoice_amount"
                                    label="Total Invoice Amount"
                                />
                                <Input
                                    data={seqData}
                                    setData={setSeqData}
                                    name="payment_delay"
                                    label="Payment Delay (Days)"
                                />
                                <Input
                                    data={seqData}
                                    setData={setSeqData}
                                    name="monthly_repayment"
                                    label="Monthly Repayment"
                                />
                                <Input
                                    data={seqData}
                                    setData={setSeqData}
                                    name="total_inflows"
                                    label="Total Inflows"
                                />
                                <Input
                                    data={seqData}
                                    setData={setSeqData}
                                    name="total_outflows"
                                    label="Total Outflows"
                                />
                            </div>
                        </div>
                    </section>
                </div>
            </div>
            <div>
                {error && (
                    <div className="text-red-600 mb-4">
                        An error occurred: {error}
                    </div>
                )}

                {result ? (
                    <div className="flex flex-col py-6 border-t border-gray-300">
                        <h3 className="text-blue-900">
                            Predicted Net Cash Flow
                        </h3>
                        <p className="text-2xl font-bold text-gray-500">
                            {result}
                        </p>
                    </div>
                ) : (
                    <button
                        type="button"
                        onClick={handleSubmit}
                        className="w-[150px] bg-blue-900 hover:bg-blue-950 px-3 py-2 rounded-sm text-white hover:text-gray-300"
                    >
                        Submit
                    </button>
                )}
            </div>
        </div>
    );
};

export default Prediction;
