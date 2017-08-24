#include<stdio.h>
#include<curses.h>
#include<time.h>
#include<stdlib.h>

int main(){
        FILE *fp = fopen("./train_t.data","w+");
        clock_t start_t,end_t;
        double result;
        int i=5;
        initscr();
start:
        while(i>0){
                start_t=clock();
                if(getch()=='\n'){
                        fprintf(fp,"\n");
                        i--;
                        goto start;
                }
                end_t=clock();
                result=(double)(end_t-end_t)/CLOCKS_PER_SEC;
                fprintf(fp,"%lf ",result);
        }
        endwin();
        return 0;
}
