# Soul

This project exists to answer a practical question before hardware becomes expensive: can a tennis ball picking robot be developed around a repeatable, inspectable simulation loop?

The current answer is intentionally modest. Build a standard hard-court world, place a simplified differential-drive picker inside it, scatter tennis balls from a deterministic seed, expose the robot through ROS topics, and keep enough validation in the repo that the same scenario can be rebuilt and checked by another person later.

## What Matters Most

Reproducibility matters more than spectacle. A seeded 50-ball court, a saved manifest, and a validator that catches broken assets are more valuable at this stage than a flashy demo that cannot be repeated.

Interfaces matter more than cleverness. `/ball_picker/cmd_vel`, `/ball_picker/odom`, sensor topics, launch arguments, model paths, and manifest structure are the skeleton that later detection, planning, pickup, and evaluation modules will attach to.

Humility matters more than simulated confidence. Gazebo can prove that the software loop is wired, that a controller can command the robot, and that scenarios can be compared. It cannot, by itself, prove real brush mechanics, real ball pickup reliability, or final product performance.

## Product Direction

The long-term target is a robot that can collect many scattered tennis balls on a real court with minimal human effort. The simulation should support that direction by making experiments cheap:

- compare strategies on the same ball distribution
- record seeds, paths, outcomes, and failure reasons
- isolate whether a failure comes from perception, planning, control, geometry, or pickup assumptions
- keep the ROS 2 structure close enough to a real robot that useful code can survive the move from simulation to hardware

## Current Stage

This repository is the P0 foundation:

- hard tennis court world
- fenced and netted boundaries
- simplified picker robot model
- tennis ball model
- deterministic ball scattering
- static P0 validator
- manual and nearest-ball autonomy launch paths

The nearest-ball autonomy demo is a smoke test for interfaces, not the final behavior. Its value is that it exercises odometry, command velocity, seeded targets, and launch composition in one place.

## Engineering Taste

Small, repeatable, and inspectable beats broad and vague. Prefer changes that improve the acceptance loop: deterministic inputs, clear outputs, validators, focused tests, and launch commands that another engineer can run.

When adding realism, add it in layers. First preserve the system-level loop. Then add pickup semantics, perception, navigation, metrics, and calibration with explicit assumptions. Each new layer should make the simulation more useful without pretending it is the real court.

The spirit of the project is a quiet one: build the simplest trustworthy world where better robot ideas can be compared, broken, repaired, and eventually carried outside.
