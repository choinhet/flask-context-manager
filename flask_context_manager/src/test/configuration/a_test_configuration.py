from dataclasses import dataclass
from typing import TYPE_CHECKING

from flask_context_manager import Configuration, Bean

if TYPE_CHECKING:
    from flask_context_manager.src.test.configuration.test_configuration import TestInstance


@dataclass
class FirstTestInstance:
    one_number: int


@dataclass
class SecondTestInstance:
    one_number: int


@Configuration
class ATestConfiguration:

    @Bean
    def im_just_a_running_bean(self, second_instance: SecondTestInstance):
        """
        This bean checks if the second instance was correctly injected.
        """
        assert second_instance.one_number is not None

    @Bean
    def first_test_instance(self, test_instance: "TestInstance") -> FirstTestInstance:
        return FirstTestInstance(1)

    @Bean
    def second_test_instance(self) -> SecondTestInstance:
        """
        Dependency for 'im_just_a_running_bean' and 'my_test_instance' from 'test_configuration'.
        """
        return SecondTestInstance(1)
