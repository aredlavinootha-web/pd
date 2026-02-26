#include <stdio.h>
#include <math.h>
int is_prime(int n){
    if(n<2)return 0;
    for(int i=2;i<=(int)sqrt(n);i++){if(n%i==0)return 0;}
    return 1;
}
int main(){printf("%d\n%d\n",is_prime(17),is_prime(20));return 0;}
