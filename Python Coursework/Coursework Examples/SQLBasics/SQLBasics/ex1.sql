
.mode column
SELECT dname
FROM dept
WHERE deptno IN (SELECT deptno
FROM emp
WHERE job="CLERK")
;