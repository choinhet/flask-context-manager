from dataclasses import dataclass

from flask_context_manager import Configuration, Bean
from flask_context_manager.src.test.configuration.test_configuration import TestInstance


@dataclass
class FirstTestInstance:
    one_number: int


@Configuration
class ATestConfiguration:

    @Bean
    def first_test_instance(self, test_instance: TestInstance) -> FirstTestInstance:
        return FirstTestInstance(1)
