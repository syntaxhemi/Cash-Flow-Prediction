import re
from typing import Protocol

from domain.exceptions import InvalidEnterpriseConfigurationError


class IEnterpriseRules(Protocol):
    def validate_configuration(
        self, *, country_code: str, base_currency: str, timezone: str
    ) -> None:
        """Validate enterprise identity and regional configuration."""
        ...


class DefaultEnterpriseRules:
    def validate_configuration(
        self, *, country_code: str, base_currency: str, timezone: str
    ) -> None:
        """Validate enterprise identity and regional configuration.

        Args:
            country_code: Three-letter uppercase country code.
            base_currency: Three-letter uppercase currency code.
            timezone: IANA timezone name.

        Raises:
            InvalidEnterpriseConfigurationError: If a value is invalid.
        """
        if not re.fullmatch(r'[A-Z]{3}', country_code):
            raise InvalidEnterpriseConfigurationError(
                'Country code must be a three-letter uppercase code.'
            )
        if not re.fullmatch(r'[A-Z]{3}', base_currency):
            raise InvalidEnterpriseConfigurationError(
                'Base currency must be a three-letter uppercase code.'
            )
        if not timezone.strip():
            raise InvalidEnterpriseConfigurationError('Timezone must not be empty.')
