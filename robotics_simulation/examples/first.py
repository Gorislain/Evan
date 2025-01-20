import pybullet as p
import time
import pybullet_data

# Подключение к PyBullet
cid = p.connect(p.SHARED_MEMORY)
if cid < 0:
    p.connect(p.GUI)

p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.resetSimulation()

p.loadURDF("plane.urdf")
kuka = p.loadURDF("kuka_iiwa/model.urdf", [0, 0, 0])

# Начальные позиции суставов
initial_joint_positions = [0, 0, 0, -1.57, 0, 1.57, 0]
for joint_index in range(p.getNumJoints(kuka)):
    p.resetJointState(kuka, joint_index, initial_joint_positions[joint_index])

# Данные о суставах
joint_limits = [
    p.getJointInfo(kuka, joint_index)[8:10]  # Мин. и макс. углы для каждого сустава
    for joint_index in range(p.getNumJoints(kuka))
]

# Функция плавного движения сустава
def move_joint(robot, joint_index, target_position, steps=100):
    current_position = p.getJointState(robot, joint_index)[0]
    for step in range(steps):
        interpolated_position = (
            current_position + (target_position - current_position) * (step + 1) / steps
        )
        p.setJointMotorControl2(
            robot, joint_index, p.POSITION_CONTROL, interpolated_position
        )
        p.stepSimulation()
        time.sleep(0.01)

# Основная функция для вращения суставов
def rotate_joints_to_limits(robot):
    for joint_index in range(p.getNumJoints(robot)):
        min_limit, max_limit = joint_limits[joint_index]

        # Вращение сустава до максимального предела
        move_joint(robot, joint_index, max_limit)
        time.sleep(0.5)

        # Возвращение сустава в исходное положение
        move_joint(robot, joint_index, initial_joint_positions[joint_index])
        time.sleep(0.5)

        # Вращение сустава до минимального предела
        move_joint(robot, joint_index, min_limit)
        time.sleep(0.5)

        # Возвращение сустава в исходное положение
        move_joint(robot, joint_index, initial_joint_positions[joint_index])
        time.sleep(0.5)

# Запуск вращения суставов
rotate_joints_to_limits(kuka)
