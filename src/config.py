from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    site_name: str = 'A Story Site'
    base_url: str = 'example.com'
    content_subdomain: str = 'www'
    cms_subdomain: str = 'author'
    search_subdomain: str = 'search'

    @validator(
        'content_subdomain',
        'cms_subdomain',
        'search_subdomain',
        pre=True,
    )
    def add_base_url(cls, v, values):
        if base_url := values.get('base_url'):
            return f'{v}.{base_url}'
        else:
            raise ValueError(
                f'Could not fetch the base_url from values list {values}'
            )


settings = Settings()
