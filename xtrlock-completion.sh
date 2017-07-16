# xtrlock(1) completion    -*- shell-script -*-

_xtrlock(){
        echo called >> /home/d0048/桌面/called.log;
        local cur="${COMP_WORDS[COMP_CWORD]}";
        local prevcur="${COMP_WORDS[COMP_CWORD]}";
        local prev="${COMP_WORDS[COMP_CWORD-1]}";
        local xtr_opts="-h --help -l --lock-user-password -p --password -e --encrypted-password -c --calculate -b --block-screen -d --delay-of-blink -n --notify"
        COMPREPLY=();
        #if [[ ${cur} == -* ]] ; then
        COMPREPLY=($(compgen -W "${xtr_opts}" "$cur" | grep "-"))
        #  return 0;
        #fi
}
complete -F _xtrlock xtrlock;
