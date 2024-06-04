from dataclasses import dataclass

from flask_context_manager import Configuration, Bean


@dataclass
class TestInstance:
    any_number: int

@Configuration
class TestConfiguration:

    @Bean
    def my_test_instance(self) -> TestInstance:
        return TestInstance(1)
