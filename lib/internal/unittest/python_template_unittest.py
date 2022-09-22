import unittest

# todo: import models unique to this service
from lib.internal.model.python_template import PythonTemplateConfig, ExamplePrivateModelConfig
# end todo

# todo: change to "import lib.internal.service.<application>_service as test_service"
import lib.internal.service.python_template_service as test_service
# end todo


# todo: modify Test Class Name to <Application>Test
class PythonTemplateTest(unittest.TestCase):
    # end todo
    def setUp(self):
        # todo: replace the following default model to be your own.
        self.python_template_model = PythonTemplateConfig(
            {
                "ExampleStr": "boop",
                "ExampleInt": 10,
                "ExampleDict": {
                    "Fruit": "apple",
                    "Vegetable": "carrot"
                },
                "ExampleFloat": 2.8,
                "ExampleCustom": {
                    "ExampleName": "Stacy",
                    "ExampleAge": 36
                }
            }
        )
        # end todo

    # todo: replace the test with your own. If more functions are being tested,
    #   then make new functions within this class.
    def test_add_int_to_float(self):
        expected = 12.8
        test_service.add_int_to_float(self.python_template_model)
        self.assertEqual(self.python_template_model.ExampleFloat, expected)

        self.python_template_model.ExampleInt = 0
        self.python_template_model.ExampleFloat = 0
        expected = 0
        test_service.add_int_to_float(self.python_template_model)
        self.assertEqual(self.python_template_model.ExampleFloat, expected)

        self.python_template_model.ExampleInt = 2.5
        self.python_template_model.ExampleFloat = 0
        expected = 2.5
        test_service.add_int_to_float(self.python_template_model)
        self.assertEqual(self.python_template_model.ExampleFloat, expected)
    # end todo


if __name__ == '__main__':
    unittest.main()
