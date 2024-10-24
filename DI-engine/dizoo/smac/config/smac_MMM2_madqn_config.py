from ding.entry import serial_pipeline
from easydict import EasyDict

agent_num = 10
collector_env_num = 4
evaluator_env_num = 8

main_config = dict(
    exp_name='smac_MMM2_madqn_seed0',
    env=dict(
        map_name='MMM2',
        difficulty=7,
        reward_only_positive=True,
        mirror_opponent=False,
        agent_num=agent_num,
        collector_env_num=collector_env_num,
        evaluator_env_num=evaluator_env_num,
        stop_value=0.999,
        n_evaluator_episode=32,
        special_global_state=True,
        manager=dict(
            shared_memory=False,
        ),
    ),
    policy=dict(
        nstep=1,
        model=dict(
            agent_num=agent_num,
            obs_shape=204,
            global_obs_shape=431,
            global_cooperation=True,
            action_shape=18,
            hidden_size_list=[256, 256],
        ),
        learn=dict(
            update_per_collect=40,
            batch_size=64,
            learning_rate=0.0005,
            clip_value=5,
            target_update_theta=0.008,
            discount_factor=0.95,
        ),
        collect=dict(
            collector=dict(
                get_train_sample=True,
            ),
            n_episode=32,
            unroll_len=20,
            env_num=collector_env_num,
        ),
        eval=dict(env_num=evaluator_env_num, evaluator=dict(eval_freq=1000, )),
        other=dict(
            eps=dict(
                type='linear',
                start=1,
                end=0.05,
                decay=100000,
            ),
            replay_buffer=dict(
                replay_buffer_size=30000,
            ),
        ),
    ),
)
main_config = EasyDict(main_config)
create_config = dict(
    env=dict(
        type='smac',
        import_names=['dizoo.smac.envs.smac_env'],
    ),
    env_manager=dict(type='base'),
    policy=dict(type='madqn'),
    collector=dict(type='episode'),
)
create_config = EasyDict(create_config)


def train(args):
    config = [main_config, create_config]
    serial_pipeline(config, seed=args.seed, max_env_step=1e7)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', '-s', type=int, default=0)
    args = parser.parse_args()

    train(args)
