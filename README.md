# workbench-dev

Developer toolkit for Claude Code: infrastructure operations, roadmap refinement, and skill authoring.

## Plugins

| Plugin | Description | Skills |
|--------|-------------|--------|
| **ops-suite** | Infrastructure operations (services, logs, databases, queues) | 9 |
| **refinery** | Roadmap refinement (tickets, sprints, designs, docs) | 11 |
| **creating-skills** | Skill authoring guide | 1 |

## Installation

```bash
/plugin marketplace add github:aldorea/workbench-dev
/plugin install ops-suite
/plugin install refinery
/plugin install creating-skills
```

## Configuration

Each plugin has a `config.example.yaml`. Copy it to `config.yaml` and fill in your values:

```bash
cp config.example.yaml config.yaml
```

## License

MIT
