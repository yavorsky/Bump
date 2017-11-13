Bump
=============

A package allows to preview and manage latest versions of [npm](https://npmjs.com)/[yarn](https://yarnpkg.com) packages easily.
Inspired by the vscode feature, but was rethought and enhanced.

For now, it allows:

- Show **latest** released package version.
- Show **next** (alpha, beta, etc) package version.
- Compare semver versions and detect whether or not current version should be updated.
- Format to **latest** or **next** version from the context menu.
- Use custom registries.
- Customize tooltip for your needs and taste.


![Demo of latest usage](https://raw.githubusercontent.com/yavorsky/Bump/master/img/preview.gif)

  ​
## Installation

#### Install Bump via Package Control

The easiest and recommended way to install Bump is using [Package Control](https://packagecontrol.io/packages/Bump).

From the **main application menu** (CMD + SHIFT + P), navigate to:

`Tools` -> `Command Palette...` -> `Package Control: Install Package`, type the word **Bump**, then select it to complete the installation.

#### Manual installation

##### via archive
1. Download and extract Bump [zip file](https://github.com/yavorsky/Bump/archive/master.zip) to your Sublime Text Packages directory (Sublime Text -> Preferences -> Browse Packages...).
2. Rename the extracted directory from `Bump-master` to `Bump`.

##### or via git clone
`git clone https://github.com/yavorsky/Bump.git $HOME/Library/Application\ Support/Sublime\ Text\ 3/Packages/Bump`

## Usage

Just install the package and focus the line with dependency in `package.json`. Bump will preview latest or next version (according to the distribution mode) of the package in the bottombar or with the tooltip.

#### Main features:

* **Focus the line** inside `dependencies`/`devDependencies`/`peerDependencies`/`optionalDependencies` block to preview latest or next version of the package. If tooltip option in settings is `false` then version will be displayed in the bottom bar.
* **Click on the version in the tooltip** to format current version to the one from tooltip.
* **Click on Bump -> Format to...** latest/next version from the context menu.
* **Choose distribution mode** to change whether or not to fetch unreleased (alpha/beta/etc) version before relaesed.


## Settings

Many options are customizable from the **Command Palette** (super + shift + p) and type **Bump**.

#### distribution_mode

Type: *String*, Default: `latest`

Command: `Choose distribution mode`.

Currently, Bump supports `latest` and `next` distribution tags. By default, the `latest` tag is used by npm to identify the current version of a package. The `next` tag is used by some projects to identify the upcoming version (alpha, beta, etc). 

With `next` mode, package trying to fetch latest version, and if no one was registered, it fallbacks to the `latest` version.


#### tooltip

Type: *Boolean*, Default: `true`

Whether or not show tooltip near the cursor. If tooltip is disabled, the version would be displayed in the botombar.


#### dependency_fields

Type: *Array*, Default: `["dependencies", "devDependencies", "peerDependencies", "optionalDependencies"]`

Field name, where Bump will search and show latest version for current package.


#### supported_filenames

Type: *Array*, Default: `["package.json"]`

Name of the files when Bump will watch out for your cursor. We haven't universal parser for all formats, but with json files it does its work.


## Key Bindings

Bump has pre-defined keyboard shortcuts. For now, it format package value on the line with the cursor.

| Command          | Key bindings    |
| ---------------- | --------------- |
| Format to latest | ALT + SHIFT + L |
| Format to next   | ALT + SHIFT + N |


------
##### For updates and more you can [follow me on twitter](https://twitter.com/yavorsky_).

## License

Bump is released under the MIT License.

Copyright (c) 2017 Artem Yavorsky.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
