standard = (
    "energy_detection",
)

special = {
    "turboSETI": "/code/bl_reservoir/turboSETI/turboSETI_env/bin/python3 -m turbo_seti.find_doppler.seti_event "
}

alg_working_directories = {
    "energy_detection": "/code/bl_reservoir/energy_detection"
}


def get_algo_type(package_name):
    if package_name == "energy_detection":
        return "Energy-Detection"


def get_algo_command_template(package_name, alg_name):
    if package_name in standard:
        return lambda input_file, output_file: \
            (f'/code/bl_reservoir/{package_name}/{package_name}_env/bin/python3'
             f' {alg_name} {input_file} {output_file}')
