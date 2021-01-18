## The Blog Engine behind the Flesh-Network

This is the Python/Flask program that drives the Flesh-Network [blog](https://flesh-network.ddns.net).

## Basic Usage

Clone this repository and make sure you have an environment with the requirements specified in `src/requirements.txt`
set up. This can easily be done using `venv`.

Then, run the `src/blog_manager.py` script to enter a console interface you can use to configure the blog.
Type `help` to see a list of available commands. To get started, you need to run `create author` and then,
to create the first post, `create post`. Type `save` to commit your changes.

After this, the posts data directory will be created in `src/blogposts/<post name>`. Edit the `post.md` file
and add resources to the `res/` folder. You can reference these resources in your `post.md` file using the
`{{ file: resource.extension }}` syntax. You can also reference posts and authors using the `{{ author: name }}`
and `{{ post: id }}` constructs.

After completing your blog post (or changing your post afterwards) return to the command line and type `compile`
to generate a `.html` file and sync resources. You should now see your blogpost appearing in the browser.
