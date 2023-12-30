# Tyr 

Porting from 2.7 to 3.11

Tyr is a habit tracker and personal data analytics app that lets you keep focus on what matters. Tyr owns none of your data. That's yours.

To spin up your own instance, or start contributing to this repo, see below.

## API Documentation

The docs are still a work in progress. 

## Setup

To deploy a new instance of Tyr, use the following instructions.

### Setup dependencies

- Node v11.15.0 (recommend using nvm)
- Ensure you have npm and gulp installed.

```
npm install -g gulp
npm install
```

### Update code configuration

Update the APP_OWNER variable in constants.py. Owner should match the Google account you logged into the console with. This will enable the application to send emails.

Create the following files by copying the templates (keep the original template files, which are used when running tests). For this step you'll need to create an oauth 2.0 web client ID from the GCP console, as per the instructions in `secrets_template.py`.

- **secrets.py** ::
  `./settings/secrets_template.py => ./settings/secrets.py`

- **client_secrets.js** ::
  `./src/js/constants/client_secrets.templates.js => ./src/js/constants/clients_secrets.js`

### Run the dev server locally

To avoid conflicts sometimes seen with gcloud and google.cloud python libs it is often helpful to run the dev server in a virtualenv. Make sure dev_appserver.py is in your path.

- `virtualenv env`
- `source env/bin/activate`
- `pip install -t lib -r requirements.txt`
- `pip install -r local.requirements.txt`
- `gcloud components update`
- `cd scripts`
- `./server.sh` (in scripts/) to start the dev server locally.
- Run `gulp` in another terminal to build JS etc
- Visit localhost:8080 to run the app, and localhost:8000 to view the local dev server console.

## Features

- Daily journal / survey
  - Configurable questions
  - Optional location pickup & mapping
  - Extract @mentions and #tags from configured open-ended responses (auto-suggest)
  - Segment analysis of journals by tag (highlight journal days with/without + show averages)
- Habit tracking ala habits app
  - With weekly targets
  - Commitments
  - Optional daily targets for 'countable' habits
- Tracking top tasks for each day
  - Analyze tasks completed: on time, late, not completed, on each given day
- Monthly/year/long-term goals
  - Goal assessment report at end of month
  - Rating for each goal monthly defined
- Ongoing Projects tracking
  - Track time of each progress increment
  - Link tasks with projects
  - Define labeled milestones
  - View 'burn-up' chart of completion progress over time
- Analysis
  - Show summary charts of all data reported to platform
- Google Assistant / Home / Facebook Messenger integration for actions like:
  - "How am I doing"
  - "What are my goals for this month"
  - "Mark 'run' as complete"
  - "Daily report"
- Reading widget
  - Show currently-reading articles / books
  - Sync quotes from evernote / Kindle
  - Sync articles from Pocket
  - Mark articles / books as favorites, and add notes
  - Quotes & articles fully searchable
- Flash card widget for spreadsheet access (e.g. random quotes, excerpts)
- Export all data to CSV

## Integrations

### Data source integrations

- Public Github commits
- Google Fit - track any activity durations by keyword
- Evernote - pull excerpts from specified notebooks
- Pocket - Sync stored articles & add notes
- Goodreads - Sync currently reading shelf
- Track any abstract data via REST API

### Setup (for separate instance)

You'll need to set up each integration you need. See below for specific instructions.

#### Pocket

Create an app at https://getpocket.com/developer/ and update settings.secrets.POCKET_CONSUMER_KEY

#### Google Home

We've used API.AI to create an agent that integrates with Google Actions / Assistant / Home. To connect Assistant with a new instance of Tyr:

1. Visit https://api.ai
2. Update the agent.json configuration file in static/Tyr-agent
3. Fill in config params in [Brackets] with your configuration / webhook URLs, etc
4. Import the agent.json to API.AI
5. Go to integrations and add and authorize 'Actions on Google'
6. Preview the integration using the web preview

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](.github/CONTRIBUTING.md)

## License

MIT License
