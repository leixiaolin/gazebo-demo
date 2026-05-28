from glob import glob
from os.path import join

from setuptools import find_packages, setup

package_name = "tennis_ball_picker_sim"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [join("resource", package_name)]),
        (join("share", package_name), ["package.xml"]),
        (join("share", package_name, "config"), glob("config/*.yaml")),
        (join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (join("share", package_name, "worlds"), glob("worlds/*.sdf")),
        (
            join("share", package_name, "models", "ball_picker"),
            glob("models/ball_picker/*.sdf") + glob("models/ball_picker/*.config"),
        ),
        (
            join("share", package_name, "models", "tennis_ball"),
            glob("models/tennis_ball/*.sdf") + glob("models/tennis_ball/*.config"),
        ),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="lxl",
    maintainer_email="498900619@qq.com",
    description=(
        "ROS 2 and Gazebo Sim MVP for a tennis ball picking robot on a "
        "court with reproducible random ball spawning."
    ),
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "print_ball_scenario = tennis_ball_picker_sim.scenario:main",
            "validate_p0_demo = tennis_ball_picker_sim.p0_validator:main",
            "nearest_ball_driver = tennis_ball_picker_sim.nearest_ball_driver:main",
        ]
    },
)
