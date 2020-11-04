standard = (
    "energy_detection",
    "dummy"
)

special = {
    "turboSETI": {
        "turboSETI":
            lambda input_file, output_file:
            ("/code/bl_reservoir/turboSETI/turboSETI_env/bin/python3"
             f" -m turbo_seti.find_doppler.seti_event {input_file} -o {output_file}")
    }
}

alg_working_directories = {
    "energy_detection": "/code/bl_reservoir/energy_detection",
    "turboSETI": "/code/bl_reservoir/turboSETI/turboSETI_env/lib/python3.6/site-packages/turbo_seti"
}


def get_algo_type(package_name):
    if package_name == "energy_detection":
        return "Energy-Detection"
    else:
        return package_name


def get_algo_command_template(package_name, alg_name):
    if package_name in standard:
        return lambda input_file, output_file: \
            (f'/code/bl_reservoir/{package_name}/{package_name}_env/bin/python3'
             f' {alg_name} {input_file} {output_file}')
    else:
        return special[package_name][alg_name]
