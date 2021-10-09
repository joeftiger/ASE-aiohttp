# ASE-aiohttp
A smol server to fulfill [these tests](http://todospecs.thing.zone/) according to [these specification](http://swagger.thing.zone/#/)

## NOTE
The test **"can create a todo, associate tags to it and remove one tag association"** fails as it expects a JSON response
from the server. **However**, this is not defined in the above mentioned specification. I've traced the exception to
[here](https://github.com/polchky/todo-tag-backend-js-spec/blob/master/js/specs.js#L401), the tests are not following
the specifications.

The test **"can create a tag, associate a todo to it, and retrieve the todo list by tag"** fails making an AJAX request.
I tried solving this by changing various browser flags to allow all local connections etc., but it doesn't solve the issue. 
It might work on your end. \
The code for this should work however.