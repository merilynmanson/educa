from typing import List

from django.contrib.contenttypes.models import ContentType

from courses.models import Test, Module


# Function finds tests objects for module
# @param module_id ID of the needed module
# @return List of tests for the module
def get_tests_for_module(module_id: int) -> List:
    return [t.item for t in Module.objects.get(id=module_id).contents.filter(
        content_type=ContentType.objects.get_for_model(Test)).all()]
