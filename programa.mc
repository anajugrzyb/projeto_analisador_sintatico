main {
var {
x:int;
y:int;
z:int;
temp:int;
}
# Ordena três números em ordem crescente
input(x);
input(y);
input(z);
if x > y then {
temp <- y;
y <- x;
x <- temp;
}
if (x > z E y <= z OU x != z) then {
temp <- z;
z <- x;
x <- temp;
}
if y > z then {
temp <- z;
z <- y;
y <- temp;
}
print("Ordem crescente:");
print(x);
print(y);
print(z);
}