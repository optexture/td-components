statusOverlay
Version: 1.0
Author: Tekt

Shows temporary or permanent status messages as an overlay
on a UI panel.

By default the panel will be non-visible. When messages are
added, the panel will show the messages and block the UI
underneath it. Once no more messages are present, the overlay
will hide itself.

Temporary messages will be shown for a limited time (controlled
by the "Temporary Message Duration" parameter), after which
they will disappear.

Static messages will be shown until they are explicitly removed.


To use, make it a child of the panel that it should cover, and
make sure that the following parameters are set (which they
will be by default when dropping in the tox):

- Depth Layer: 1
- Horizontal Mode: Fill
- Vertical Mode: Fill
- Parent Alignment: Ignore
- Display: False


To add a temporary message, either call `.AddMessage('some text')`
or put the text in the "Message to Add" parameter and click the
"Add Temporary Message" pulse parameter.

To add a static message, either call `.AddStaticMessage('some text')`
or use the "Add Static Message" pulse parameter. Calling the method
will return an identifier that can later be passed to
`.ClearMessage(messageId)`.

To remove all messages, either call `.ClearAllMessages()` or use
the "Clear Messages" pulse parameter.