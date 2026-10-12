Here are some useful Linux terminal tricks (astuces) like `\` for continuing a command on a new line. These are especially useful when working with Bitcoin Core, Docker, Git, Python, and other development tools.

## 1. Command-line tricks

### Astuce 1 — `\` : Continue a command on the next line

Use it to make long commands easier to read.

```
bitcoin-cli \
  -conf=/opt/bitcoin/bitcoin.conf \
  -regtest \
  -rpcwallet=miner \
  getwalletinfo
```

The shell treats it as one command.

### Astuce 2 — `&&` : Execute the next command only if the previous succeeds

```
mkdir bitcoin-lab && cd bitcoin-lab
```

- `mkdir bitcoin-lab` creates the directory.
- `cd bitcoin-lab` runs only if the directory creation succeeds.

### Astuce 3 — `;` : Execute commands one after another

```
pwd; ls; whoami
```

Each command runs even if the previous command fails.

### Astuce 4 — `||` : Execute the next command if the previous fails

```
cd /wrong/path || echo "Directory not found"
```

If `cd` fails, the error message is displayed.

### Astuce 5 — `#` : Write comments in shell scripts

```
# Display Bitcoin wallet information
bitcoin-cli -regtest getwalletinfo
```

The shell ignores the comment.

### Astuce 6 — `>` : Redirect output into a file

```
bitcoin-cli -regtest getwalletinfo > wallet.txt
```

Saves the output in `wallet.txt`, replacing its previous contents.

### Astuce 7 — `>>` : Append output to a file

```
date >> commands.log
```

Adds the current date to the end of `commands.log` instead of replacing its contents.

### Astuce 8 — `|` : Pipe output into another command

```
ls -l | grep bitcoin
```

The output of `ls -l` becomes the input of `grep`, which filters lines containing `bitcoin`.

### Astuce 9 — `$()` : Use the output of one command inside another

```
echo "Current directory: $(pwd)"
```

The shell executes `pwd` and inserts its output into the `echo` command.

### Astuce 10 — `*` : Match multiple filenames

```
ls *.conf
```

Lists files ending in `.conf` in the current directory.

## 2. Useful keyboard shortcuts

These work in many Bash terminals.

| Shortcut   | Action                                                    |
| ---------- | --------------------------------------------------------- |
| `Ctrl + C` | Interrupt the current foreground command.                 |
| `Ctrl + L` | Clear the terminal display.                               |
| `Ctrl + A` | Move the cursor to the beginning of the line.             |
| `Ctrl + E` | Move the cursor to the end of the line.                   |
| `Ctrl + U` | Delete text from the cursor to the beginning of the line. |
| `Ctrl + K` | Delete text from the cursor to the end of the line.       |
| `Ctrl + W` | Delete the previous word.                                 |
| `Ctrl + R` | Search through command history.                           |
| `Tab`      | Autocomplete commands, paths, and filenames.              |
| `↑` / `↓`  | Navigate through previous commands.                       |

## 3. More advanced tricks

Astuce 11 — `{ }` : Group commands

```
{ pwd; ls; } > result.txt
```

Runs both commands in a group and redirects their combined standard output to `result.txt`.

Astuce 12 — `2>` : Redirect error messages

```
ls /wrong/path 2> errors.txt
```

Saves error output in `errors.txt`.

Astuce 13 — `tee` : Display and save output

```
bitcoin-cli -regtest getwalletinfo | tee wallet.txt
```

Shows the output in the terminal and writes it to `wallet.txt`.

Astuce 14 — `!!` : Repeat the previous command

```
!!
```

Executes the last command again. Be careful when repeating commands that change files or system settings.

Astuce 15 — `~` : Refer to your home directory

```
cd ~
```

Takes you to your home directory, usually `/home/your_username`.

Astuce 16 — `-` : Return to the previous directory

```
cd -
```

Switches back to the previous working directory and prints its path.

## 4. Bonus: Useful with Bitcoin Core

You can combine several of these techniques:

```
bitcoin-cli \
  -conf=/opt/bitcoin/bitcoin.conf \
  -regtest \
  -rpcwallet=miner \
  getwalletinfo | tee wallet-info.json
```

This command uses `\` for readability and `| tee` to display and save the wallet information.

One important distinction: `\` continues a command across lines, while `|` sends output from one command to another. They look similar, but their jobs are different.