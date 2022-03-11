# Setup Your Editor for Auto-completion and instantaneous validation

## Visual Studio Code (VSCode)
- Install the [YAML][1] plugin.
- Open `ocp-build-data` project.
- Add the following config options to `.vscode/settings.json`:
    ```json
    {
        "yaml.schemas": {
            "/path/to/json_schemas/releases.schema.json": "/releases.yml",
        }
    }
    ```
- Open `releases.yml`.

## PyCharm (or other Intellij IDEA based IDEs)
- Open `ocp-build-data` project.
- Go to `Preferences | Languages & Frameworks | Schemas and DTDs | JSON Schema Mappings`.
- Click `+`. Add a JSON schema mapping as the following:
  - *Name* Choose a friendly name. e.g. `OCP releases`
  - *Schema file or URL* The path to `json_schemas/releases.schema.json`
  - *Schema version* Choose `JSON Schema version 7`
  - Click `+`, choose `Add file`, type `releases.yml`, and press `Return`.
- Open `releases.yml`.


[1]: https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml
