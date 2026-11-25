# Multi-user news blog

Live discovery revision 6. Source records: news-blog-brief, whole-blog-and-editor-rights, author-publishes-directly, news-index-request, five-use-cases-confirmed, article-date-note.

The five use cases are agreed. Screens and navigation await replay. Each scenario begins in its named role. The stories, author names, publication dates, and prefilled new story are example content. One new story can be tried per replay. Published changes are shared among role examples in the same open viewer and reset on reload.

```yaml
scope: Multi-user news blog
scenarios:
  browse-index:
    capability: Browse the news index and choose a story
    start: reader-index
    steps:
    - read-library
  read-story:
    capability: Read a story and return to the news index
    start: reader-market
    steps:
    - return
  publish-story:
    capability: Write a story and publish it on the news index
    start: author-index
    steps:
    - create
    - publish
    - read-garden
    - return
  edit-own-story:
    capability: Edit your own published story
    start: author-index
    steps:
    - read-library
    - edit
    - save
    - return
  edit-another-story:
    capability: Edit another author’s story as a special editor
    start: editor-index
    steps:
    - read-market
    - edit
    - save
    - return
screens:
  reader-index:
    title: News index
    elements:
    - type: text
      value: Guest reader
    actions:
      read-library:
        label: Read
        go: reader-library
        row: The library opens a Sunday reading room
        bind: library-title
      read-market:
        label: Read
        go: reader-market
        row: Saturday market moves to the square
        bind: market-title
      read-garden:
        label: Read
        go: reader-garden
        row: Community garden adds new plots
        bind: garden-title
        visibleAfter: garden-published
  reader-library:
    title: Article
    elements:
    - type: text
      value: The library opens a Sunday reading room
      bind: library-title
    - type: text
      value: By Mira Lane
    - type: text
      value: Published 24 November 2026
    - type: text
      value: The east reading room will open on Sundays this spring. Volunteers will
        host an afternoon book exchange.
      bind: library-body
    actions:
      return:
        label: Back to news
        go: reader-index
  reader-market:
    title: Article
    elements:
    - type: text
      value: Saturday market moves to the square
      bind: market-title
    - type: text
      value: By Ravi Shah
    - type: text
      value: Published 25 November 2026
    - type: text
      value: Stallholders are moving to the town square this Saturday while repairs
        continue on Market Street.
      bind: market-body
    actions:
      return:
        label: Back to news
        go: reader-index
  reader-garden:
    title: Article
    elements:
    - type: text
      value: Community garden adds new plots
      bind: garden-title
    - type: text
      value: By Mira Lane
    - type: text
      value: Published 26 November 2026
    - type: text
      value: Residents can sign up for the new garden plots at the neighborhood center
        on Friday.
      bind: garden-body
    actions:
      return:
        label: Back to news
        go: reader-index
  author-index:
    title: News index
    elements:
    - type: text
      value: Mira Lane · Author
    actions:
      read-library:
        label: Read
        go: author-library
        row: The library opens a Sunday reading room
        bind: library-title
      read-market:
        label: Read
        go: author-market
        row: Saturday market moves to the square
        bind: market-title
      read-garden:
        label: Read
        go: author-garden
        row: Community garden adds new plots
        bind: garden-title
        visibleAfter: garden-published
      create:
        label: Write a story
        go: write-story
  author-library-edit:
    title: Edit story
    elements:
    - type: text
      value: Mira Lane · Author
    - type: form
      label: Story
      fields:
      - type: text-field
        label: Headline
        example: The library opens a Sunday reading room
        bind: library-title
      - type: text-field
        label: Article text
        example: The east reading room will open on Sundays this spring. Volunteers
          will host an afternoon book exchange.
        bind: library-body
    actions:
      save:
        label: Save changes
        go: author-library
        commit: true
      cancel:
        label: Cancel
        go: author-library
  author-library:
    title: Article
    elements:
    - type: text
      value: The library opens a Sunday reading room
      bind: library-title
    - type: text
      value: By Mira Lane
    - type: text
      value: Published 24 November 2026
    - type: text
      value: The east reading room will open on Sundays this spring. Volunteers will
        host an afternoon book exchange.
      bind: library-body
    actions:
      edit:
        label: Edit story
        go: author-library-edit
      return:
        label: Back to news
        go: author-index
  author-market:
    title: Article
    elements:
    - type: text
      value: Saturday market moves to the square
      bind: market-title
    - type: text
      value: By Ravi Shah
    - type: text
      value: Published 25 November 2026
    - type: text
      value: Stallholders are moving to the town square this Saturday while repairs
        continue on Market Street.
      bind: market-body
    actions:
      return:
        label: Back to news
        go: author-index
  author-garden-edit:
    title: Edit story
    elements:
    - type: text
      value: Mira Lane · Author
    - type: form
      label: Story
      fields:
      - type: text-field
        label: Headline
        example: Community garden adds new plots
        bind: garden-title
      - type: text-field
        label: Article text
        example: Residents can sign up for the new garden plots at the neighborhood
          center on Friday.
        bind: garden-body
    actions:
      save:
        label: Save changes
        go: author-garden
        commit: true
      cancel:
        label: Cancel
        go: author-garden
  author-garden:
    title: Article
    elements:
    - type: text
      value: Community garden adds new plots
      bind: garden-title
    - type: text
      value: By Mira Lane
    - type: text
      value: Published 26 November 2026
    - type: text
      value: Residents can sign up for the new garden plots at the neighborhood center
        on Friday.
      bind: garden-body
    actions:
      edit:
        label: Edit story
        go: author-garden-edit
      return:
        label: Back to news
        go: author-index
  editor-index:
    title: News index
    elements:
    - type: text
      value: Jo Reed · Special editor
    actions:
      read-library:
        label: Read
        go: editor-library
        row: The library opens a Sunday reading room
        bind: library-title
      read-market:
        label: Read
        go: editor-market
        row: Saturday market moves to the square
        bind: market-title
      read-garden:
        label: Read
        go: editor-garden
        row: Community garden adds new plots
        bind: garden-title
        visibleAfter: garden-published
  editor-library-edit:
    title: Edit story
    elements:
    - type: text
      value: Jo Reed · Special editor
    - type: form
      label: Story
      fields:
      - type: text-field
        label: Headline
        example: The library opens a Sunday reading room
        bind: library-title
      - type: text-field
        label: Article text
        example: The east reading room will open on Sundays this spring. Volunteers
          will host an afternoon book exchange.
        bind: library-body
    actions:
      save:
        label: Save changes
        go: editor-library
        commit: true
      cancel:
        label: Cancel
        go: editor-library
  editor-library:
    title: Article
    elements:
    - type: text
      value: The library opens a Sunday reading room
      bind: library-title
    - type: text
      value: By Mira Lane
    - type: text
      value: Published 24 November 2026
    - type: text
      value: The east reading room will open on Sundays this spring. Volunteers will
        host an afternoon book exchange.
      bind: library-body
    actions:
      edit:
        label: Edit story
        go: editor-library-edit
      return:
        label: Back to news
        go: editor-index
  editor-market-edit:
    title: Edit story
    elements:
    - type: text
      value: Jo Reed · Special editor
    - type: form
      label: Story
      fields:
      - type: text-field
        label: Headline
        example: Saturday market moves to the square
        bind: market-title
      - type: text-field
        label: Article text
        example: Stallholders are moving to the town square this Saturday while repairs
          continue on Market Street.
        bind: market-body
    actions:
      save:
        label: Save changes
        go: editor-market
        commit: true
      cancel:
        label: Cancel
        go: editor-market
  editor-market:
    title: Article
    elements:
    - type: text
      value: Saturday market moves to the square
      bind: market-title
    - type: text
      value: By Ravi Shah
    - type: text
      value: Published 25 November 2026
    - type: text
      value: Stallholders are moving to the town square this Saturday while repairs
        continue on Market Street.
      bind: market-body
    actions:
      edit:
        label: Edit story
        go: editor-market-edit
      return:
        label: Back to news
        go: editor-index
  editor-garden-edit:
    title: Edit story
    elements:
    - type: text
      value: Jo Reed · Special editor
    - type: form
      label: Story
      fields:
      - type: text-field
        label: Headline
        example: Community garden adds new plots
        bind: garden-title
      - type: text-field
        label: Article text
        example: Residents can sign up for the new garden plots at the neighborhood
          center on Friday.
        bind: garden-body
    actions:
      save:
        label: Save changes
        go: editor-garden
        commit: true
      cancel:
        label: Cancel
        go: editor-garden
  editor-garden:
    title: Article
    elements:
    - type: text
      value: Community garden adds new plots
      bind: garden-title
    - type: text
      value: By Mira Lane
    - type: text
      value: Published 26 November 2026
    - type: text
      value: Residents can sign up for the new garden plots at the neighborhood center
        on Friday.
      bind: garden-body
    actions:
      edit:
        label: Edit story
        go: editor-garden-edit
      return:
        label: Back to news
        go: editor-index
  write-story:
    title: Write a story
    elements:
    - type: text
      value: Mira Lane · Author
    - type: form
      label: Story
      fields:
      - type: text-field
        label: Headline
        example: Community garden adds new plots
        bind: garden-title
      - type: text-field
        label: Article text
        example: Residents can sign up for the new garden plots at the neighborhood
          center on Friday.
        bind: garden-body
    actions:
      publish:
        label: Publish
        go: author-index
        commit: true
        reveal: garden-published
      cancel:
        label: Cancel
        go: author-index
```
