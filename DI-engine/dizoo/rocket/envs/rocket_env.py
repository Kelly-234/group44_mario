from typing import Any, List, Union, Optional
import time
import gym
import copy
import numpy as np
from easydict import EasyDict
from ding.envs import BaseEnv, BaseEnvTimestep
from ding.torch_utils import to_ndarray, to_list
from ding.utils import ENV_REGISTRY
from ding.envs import ObsPlusPrevActRewWrapper
from rocket_recycling.rocket import Rocket
import os
import imageio


@ENV_REGISTRY.register('rocket')
class RocketEnv(BaseEnv):

    def __init__(self, cfg: dict = {}) -> None:
        self._cfg = cfg
        self._init_flag = False
        self._save_replay = False
        self._observation_space = gym.spaces.Box(
            low=float("-inf"),
            high=float("inf"),
            shape=(8, ),
            dtype=np.float32
        )
        self._action_space = gym.spaces.Discrete(9)
        self._action_space.seed(0)  # default seed
        self._reward_space = gym.spaces.Box(low=float("-inf"), high=float("inf"), shape=(1, ), dtype=np.float32)

    def reset(self) -> np.ndarray:
        if not self._init_flag:
            self._env = Rocket(task=self._cfg.task, max_steps=self._cfg.max_steps)
            self._init_flag = True
        if hasattr(self, '_seed') and hasattr(self, '_dynamic_seed') and self._dynamic_seed:
            np_seed = 100 * np.random.randint(1, 1000)
            self._env.seed(self._seed + np_seed)
            self._action_space.seed(self._seed + np_seed)
        elif hasattr(self, '_seed'):
            self._env.seed(self._seed)
            self._action_space.seed(self._seed)
        self._final_eval_reward = 0
        obs = self._env.reset()
        obs = to_ndarray(obs)
        if self._save_replay:
            self._frames = []
        return obs

    def close(self) -> None:
        if self._init_flag:
            self._env.close()
        self._init_flag = False

    def seed(self, seed: int, dynamic_seed: bool = True) -> None:
        self._seed = seed
        self._dynamic_seed = dynamic_seed
        np.random.seed(self._seed)

    def step(self, action: Union[int, np.ndarray]) -> BaseEnvTimestep:
        if isinstance(action, np.ndarray) and action.shape == (1, ):
            action = action.squeeze()  # 0-dim array

        obs, rew, done, info = self._env.step(action)
        self._env.render()
        self._final_eval_reward += rew

        if self._save_replay:
            self._frames.extend(self._env.render())
        if done:
            info['final_eval_reward'] = self._final_eval_reward
            if self._save_replay:
                path = os.path.join(
                    self._replay_path, '{}_episode.gif'.format(self._save_replay_count)
                )
                self.display_frames_as_gif(self._frames, path)
                self._save_replay_count += 1
        obs = to_ndarray(obs)
        # wrapped to be transfered to a array with shape (1,)
        rew = to_ndarray([rew]).astype(np.float32)  
        return BaseEnvTimestep(obs, rew, done, info)

    def enable_save_replay(self, replay_path: Optional[str] = None) -> None:
        if replay_path is None:
            replay_path = './video'
        self._save_replay = True
        if not os.path.exists(replay_path):
            os.makedirs(replay_path)
        self._replay_path = replay_path
        self._save_replay_count = 0

    def random_action(self) -> np.ndarray:
        random_action = self.action_space.sample()
        random_action = to_ndarray([random_action], dtype=np.int64)
        return random_action

    @property
    def observation_space(self) -> gym.spaces.Space:
        return self._observation_space

    @property
    def action_space(self) -> gym.spaces.Space:
        return self._action_space

    @property
    def reward_space(self) -> gym.spaces.Space:
        return self._reward_space

    def __repr__(self) -> str:
        return "DI-engine Rocket Env"

    @staticmethod
    def display_frames_as_gif(frames: list, path: str) -> None:
        imageio.mimsave(path, frames, fps=20)
