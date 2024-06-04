from dataclasses import dataclass
from typing import TYPE_CHECKING

from flask_context_manager import Configuration, Bean

if TYPE_CHECKING:
    from flask_context_manager.src.test.configuration.a_test_configuration import SecondTestInstance


@dataclass
class TestInstance:
    any_number: int


@Configuration
class TestConfiguration:

    @Bean
    def my_test_instance(self, second_instance: "SecondTestInstance") -> TestInstance:
        """
        Depends on 'second instance' from 'a_test_configuration' and
        provides 'test_instance' which is a dependency requested by 'first_test_instance' from 'a_test_configuration'.
        """
        assert second_instance is not None
        return TestInstance(1)
