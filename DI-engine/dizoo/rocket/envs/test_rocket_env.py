import pytest
import numpy as np
from dizoo.rocket.envs.rocket_env import RocketEnv
from easydict import EasyDict


@pytest.mark.envtest
class TestRocketEnv:

    def test_hover(self):
        env = RocketEnv(EasyDict({'task': 'hover', 'max_steps': 800}))
        env.seed(314, dynamic_seed=False)
        assert env._seed == 314
        obs = env.reset()
        assert obs.shape == (8,)
        for _ in range(5):
            env.reset()
            np.random.seed(314)
            print('=' * 60)
            for i in range(10):
                # Both ``env.random_action()``, and utilizing ``np.random`` as well as action space,
                # can generate legal random action.
                if i < 5:
                    random_action = np.array([env.action_space.sample()])
                else:
                    random_action = env.random_action()
                timestep = env.step(random_action)
                print('timestep', timestep, '\n')
                assert isinstance(timestep.obs, np.ndarray)
                assert isinstance(timestep.done, bool)
                assert timestep.obs.shape == (8,)
                assert timestep.reward.shape == (1,)
                assert timestep.reward >= env.reward_space.low
                assert timestep.reward <= env.reward_space.high
        print(env.observation_space, env.action_space, env.reward_space)
        env.close()
