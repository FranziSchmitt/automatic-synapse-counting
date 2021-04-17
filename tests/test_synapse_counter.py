import pytest
from synapse_counting.synapse_counter import SynapseCounter


class TestSynapseCounter:
    @pytest.mark.parametrize(
        ["input_path", "number_of_images", "expected_voxel_height"],
        [('tests/test_data/3-56_CO_63x2', 22, 0.116257)
         ]
    )
    def test__load_data_expect_image_sequence(self, input_path, number_of_images, expected_voxel_height):
        pass

    def test__data_loader_can_handle_strings(self):
        input_path = 'tests/test_data/3-56_CO_63x2'
        counter = SynapseCounter()
        counter.count_synapses(input_path)


