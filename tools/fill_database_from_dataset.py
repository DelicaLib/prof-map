import asyncio

import click
import pandas as pd

from dependencies.postgres.pool import PostgresPool
from dependencies.settings import Settings
from main import prepare_container
from utils.parse_config import parse_config

insert_query_prof = """
        INSERT INTO vacancy (id, name) 
        VALUES ($1, $2)
        """
insert_query_skills = """
        INSERT INTO skill (name) 
        VALUES ($1)
        """


async def fill_bd(path: str, pool) -> None:
    df = pd.read_csv(path, encoding='UTF-8')
    ids = list(df['id'])
    names = list(df['name'])
    skills = list(df['skills'])
    skills_set = set()
    for skill in skills:
        skil_list = skill.strip('{}').replace("'", "").split(',')
        for s in skil_list:
            skills_set.add(s)

    async with pool.acquire() as connection:
        async with connection.transaction():
            for skill in skills_set:
                await connection.execute(insert_query_skills, skill)
            for id_, name in zip(ids, names):
                await connection.execute(insert_query_prof, id_, name)


@click.command()
@click.option('--config', help='Path to config', required=True)
@click.option('--dataset', help='Path to dataset', required=True)
def main(config: str, dataset: str):
    settings_dict = parse_config(config)
    prepare_container(settings_dict)
    pool = PostgresPool(Settings(**settings_dict))

    async def run():
        await pool.connect()
        await fill_bd(dataset, pool)
    asyncio.run(run())


if __name__ == "__main__":
    main()
