import os

from flamingo.core.utils.string import slugify, split


class Authors:
    THEME_PATHS = [os.path.join(os.path.dirname(__file__), "theme")]

    def contents_parsed(self, context):
        content_key = getattr(context.settings, "I18N_CONTENT_KEY", "id")

        for content in context.contents:
            if content["authors"]:
                content["authors"] = split(content["authors"])

            else:
                content["authors"] = []

        authors = sorted(list(set(sum(context.contents.values("authors"), []))))

        # gen author pages
        for author in authors:
            output = os.path.join(f"authors/{slugify(author)}.html")

            context.contents.add(
                **{
                    content_key: f"_author/{author}",
                    "output": output,
                    "url": "/" + output,
                    "author": author,
                    "template": "author.html",
                }
            )
