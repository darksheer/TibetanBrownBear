"""Detail Yeti's Yara rule object structure."""
import base64

from marshmallow import fields, post_load
import yara

from yeti.core.errors import ValidationError
from .indicator import Indicator, IndicatorSchema


class YaraRuleSchema(IndicatorSchema):
    """(De)serialization marshmallow.Schema for Malware objects."""
    pattern = fields.String(required=True, allow_none=True)

    @post_load
    def load_yara_rule(self, rule_object):
        """Load a Yara rule object from its JSON representation.

        Returns:
          The Yara rule object.
        """
        if rule_object.pattern:
            rule_object.compiled_rule = yara.compile(source=rule_object.pattern)
        return rule_object


class YaraRule(Indicator):
    """Yara rule Yeti object.

    Attributes:
      family: list(str), the families this malware belongs to.
    """

    schema = YaraRuleSchema
    _collection_name = 'indicators'

    type = 'indicator.yararule'
    pattern = ''
    compiled_rule = None

    def is_valid(self):
        Indicator.is_valid(self)
        if not isinstance(self.pattern, str):
            raise ValidationError('.pattern must be str')
        try:
            yara.compile(source=self.pattern)
        except (yara.SyntaxError, yara.Error) as err:
            raise ValidationError(
                'Could not compile yara rule: {0:s}'.format(str(err)))
        return True

    def match(self, obj):
        """Matches a Yara rule against a binary stream.

        Args:
          obj: Binary data to match the Yara rule against.

        Returns:
          The matching strings if found, None otherwise.
        """
        matches = self.compiled_rule.match(data=obj)
        if matches:
            result = {'name': self.name, 'details': []}
            for match in matches:
                for offset, name, bytes_ in match.strings:
                    result['details'].append({
                        'offset': offset,
                        'name': name,
                        'bytes': {'b64': str(base64.b64encode(bytes_))},
                    })
            return result
        return None

Indicator.datatypes[YaraRule.type] = YaraRule
