from pathlib import Path

import pytest
from synapse_counting.synapse_counter import SynapseCounter, VOXEL_HEIGHT

path_to_repo = Path.cwd().parent
path_to_test_data = path_to_repo / 'tests/test_data'


class TestSynapseCounter:
    @pytest.mark.parametrize(
        ["input_path", "number_of_images", "expected_voxel_height"],
        [('3-56_CO_63x2', 22, 0.116257)
         ]
    )
    def test_load_data_expect_image_sequence(self, input_path, number_of_images, expected_voxel_height):
        input_file = path_to_test_data / input_path
        counter = SynapseCounter()
        counter.count_synapses(filepath=input_file, visualize_result=False)
        assert len(counter.image_sequence) == number_of_images
        assert counter.meta_data[VOXEL_HEIGHT] == expected_voxel_height

    def test_data_loader_can_handle_strings(self):
        input_path = str(path_to_test_data / '3-56_CO_63x2')
        counter = SynapseCounter()
        counter.count_synapses(input_path, visualize_result=False)
        assert counter.image_sequence

    def test_data_loader_raises_error_if_dir_not_exist(self):
        input_path = str(path_to_test_data / '3-58_CO_63x2')
        counter = SynapseCounter()
        with pytest.raises(ValueError) as err:
            counter.count_synapses(input_path, visualize_result=False)
            error_message = f'The path you provided does not exist: {input_path}.'
            assert err.value == error_message

    def test_data_loader_error_if_no_images_found(self):
        input_path = str(path_to_test_data / '3-56_CO_63x2_no_images')
        counter = SynapseCounter()
        with pytest.raises(ValueError) as err:
            counter.count_synapses(input_path, visualize_result=False)
            error_message = f'Could not find any tif image files in {input_path}.'
            assert err.value == error_message

    def test_data_loader_error_if_no_metadata_found(self):
        input_path = str(path_to_test_data / '3-56_CO_63x2_no_metadata')
        counter = SynapseCounter()
        with pytest.raises(ValueError) as err:
            counter.count_synapses(input_path, visualize_result=False)
            error_message = f'Could not find a metadata file in {input_path}. Expected to find a .txt file there.'
            assert err.value == error_message
