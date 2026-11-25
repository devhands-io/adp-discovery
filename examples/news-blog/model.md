# News blog data model for review

Workspace `news-blog`, discovery revision 7. Confirmed for the five agreed scenarios. Confirmation: `blog-data-model-confirmation`.

| Concept | Confirmed facts and relationships | Where they matter |
| --- | --- | --- |
| Story | Headline, article text, one author, date first published | The index lists published headlines. The article page displays headline, byline, publication date and text. |
| Contributor | Display name and editing role. One contributor can author many stories. | The byline identifies the author. Ownership permits editing one's own stories. A special editor may edit any story. |

| Scenario | Data to check |
| --- | --- |
| 1 · Browse the news index | Each published headline opens its corresponding story. |
| 2 · Read a story | The selected story shows its headline, text, author and publication date. |
| 3 · Publish a story | The author supplies headline and text. Publication assigns the signed-in author and the first publication date; the story then appears on the index. |
| 4 · Edit your own story | Match the signed-in author to story ownership; save the revised headline or text. |
| 5 · Edit another author's story | The special editor may revise the story. Editing preserves the original author and publication date. |

Evidence: `news-blog-brief`, `whole-blog-and-editor-rights`, `author-publishes-directly`, `news-index-request`, `five-use-cases-confirmed`, `article-date-note`.

The reader asked for a date on the article page. The modeler confirmed that it is the first publication date, assigned on publishing and preserved after edits.
