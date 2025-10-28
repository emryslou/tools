dirname=$(dirname $(dirname $(readlink -f $0)))
project_name=$(basename $dirname)

echo "======================Running tests...================================="
python -m pytest -q $dirname/src/tests -v
echo "======================Tests passed.====================================="

echo "======================Building package structure...======================="
tree $dirname -I dist -I __pycache__ -I dist -I build -I *.egg-info -I config -I data -I *.log > $dirname/src/meta/package_structure.txt
sed -i "s#$dirname#$project_name#g" $dirname/src/meta/package_structure.txt > $dirname/src/meta/$project_name.txt
rm $dirname/src/meta/$project_name.txt
echo "======================Package structure built.==========================="

echo "======================Building wheel...=================================="
python $dirname/setup.py bdist_wheel --dist-dir $dirname/dist
echo "======================Wheel built.======================================"
