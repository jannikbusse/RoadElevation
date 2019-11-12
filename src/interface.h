// file interface.h

struct laneLink
{
    int from;
    int to;
};

struct connection
{
    int id;
    int from;
    int to;
    string contactPoint = "start";
    int fromLane;
    int toLane;
};

struct junction
{
    int id;
    vector<connection> connections;
};

struct roadmark
{
    double s = 0;
    string type = "solid";
    string weight = "standard";
    string color = "white";
    double width = 0.15;
};

struct width
{
    double s = 0;
    double a = 3.5;
    double b = 0;
    double c = 0;
    double d = 0;
};

struct offset
{
    double a = 0;
    double b = 0;
    double c = 0;
    double d = 0;
};

struct material
{
    double s = 0;
    string surface = "asphalt";
    double friction = 0.8;
    double roughness = 0.015;
};

struct lane
{
    int id;
    string type = "driving";
    int turn = 0;
    int level = 0;
    double speed = 0;
    width w;
    roadmark rm;
    material m;
    int preId = 0;
    int sucId = 0;
};

struct laneSection
{
    int id;
    double s = 0;
    vector<lane> lanes;

    offset o;
};

struct geometry
{
    int type;
    double s;
    double x;
    double y;
    double hdg;
    double length;
    double c;
    double c1;
    double c2;
};

struct link
{
    string elementType = "road";
    int elementId = -1;
    string contactPoint = "start";
};

struct object
{
    int id = -1;
    string type;
    double s = 0;
    double t = 0;
    double z = 0;
    double hdg = 0;
    string orientation = "none";
    double length = 0;
    double width = 0;
    double height = 0;

    bool repeat = false;
    double len = 0;
    double distance = 0;
};

struct Signal
{
    int id = -1;
    int rule = -1;

    string type;
    string subtype = "-1";
    double value = -1;
    double s = 0;
    double t = 0;
    double z = 0;
    string orientation = "none";
    double width = 0;
    double height = 0;
    bool dynamic;
    string country = "OpenDRIVE";
};

struct control
{
    vector<Signal> signals;
    int id = -1;
};

struct road
{
    double length = 0;
    int id = -1;
    int junction = -1;
    string type = "town";

    link predecessor;
    link successor;

    vector<geometry> geometries;
    vector<laneSection> laneSections;
    vector<object> objects;
    vector<Signal> signals;
};

struct roadNetwork
{
    string file;
    vector<road> roads;
    vector<junction> junctions;
    vector<control> controller;
    int nSignal = 0;
    int nSegment = 0;
    int versionMajor = 1;
    int versionMinor = 5;
};