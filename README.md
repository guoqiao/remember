# Remember

A cli tool helps to remember words when you open your terminal.

# why I need it

Assume you use a cli dict, e.g.: [wudao-dict](https://github.com/ChestnutHeng/Wudao-dict)

You lookup words in terminal like:

    > $ wudao dehydration                                                                                                                [±master ●]
    dehydration
    英 [ˌdiːhaɪˈdreɪʃn]  美 [ˌdiːhaɪˈdreɪʃn]
    n. 脱水

    1. [例] Early dehydration – no signs or symptoms.  早期脱水——无迹象或无症状。
    2. [例] There is no specific treatment for yellow fever, only supportive care to treat dehydration and fever.  对黄热病没有特效治疗方法，支持性治疗只是治疗脱水和发热。
    3. [例] Literally. Tears not only lubricate our eyeballs and eyelids, they also prevent dehydration of our various mucous membranes.  从字面上看，泪水不仅润滑我们的眼球和眼睑，还可以防止各种黏膜脱水。


Normally you are not likely to remember this new word with a one-off lookup.

This tool can save this lookup into sqlite db, and show it again in your terminal
at multiple interval days(e.g.: 1, 3, 7, 30, 60), to help you finally remember it.

# how to use

0. install deps:

    ```
    sudo python3 -m pip install -r requirements.txt
    ```

1. link this script into `$PATH`


    ```
    cd ~/bin  # I assume it's in your $PATH
    ln -s ~/git/remember/remember.py remember
    ```


2. create a wrapper for your cli dict, e.g.: `~/bin/wd`

    ```
    #!/bin/bash
    wudao "$@" | tee /dev/tty | remember --input -
    ```


3. add this line into your `.bashrc/.zshrc`:

    ```
    remember --pop
    ```

From now on, when you lookup word with the wrapper `wd`,
it will be saved to db, and reminders are scheduled at multiple intervals.
When you open you terminal everyday, it will show you the due reminders.
