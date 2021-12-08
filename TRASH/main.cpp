#include <iostream>
#include <string>
#include <fstream>
#include <sstream>

using namespace std;

int main(int, char **)
{
    // note the use of normalized version (no carriage returns allowed!!)
    ifstream file("case1-input-normal.txt");

    // skip first line
    file.ignore(256, '\n');

    int i = 0;
    string line;

    // iterate over each line
    if (getline(file, line))
    {
        istringstream iss(line);
        string result;

        // iterate over each entry within a line
        while (getline(iss, result, '\t'))
        {
            cout << i << " " << stof(result) << endl;
            i++;
        }
    }
}
