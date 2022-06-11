load('usborder.mat','x','y','xx','yy');
rng(3,'twister') % Makes stops in Maine & Florida, and is reproducible
nStops = 200; % You can use any number, but the problem size scales as N^2
stopsLon = zeros(nStops,1); % Allocate x-coordinates of nStops
stopsLat = stopsLon; % Allocate y-coordinates
n = 1;
while (n <= nStops)
    xp = rand*1.5;
    yp = rand;
    if inpolygon(xp,yp,x,y) % Test if inside the border
        stopsLon(n) = xp;
        stopsLat(n) = yp;
        n = n+1;
    end
end

% Hier werden alle Paarungen der Stops erstellt.
idxs = nchoosek(1:nStops,2);

% Hier wird die Entferungen der einzelen Paare zueinander berechnet
dist = hypot(stopsLat(idxs(:,1)) - stopsLat(idxs(:,2)), stopsLon(idxs(:,1)) - stopsLon(idxs(:,2)));
lendist = length(dist);

% idxs(:,1) = Erste Spalte von idxs || idxs(:,2) = Zweite Spalte von idxs
G = graph(idxs(:,1),idxs(:,2));

figure
hGraph = plot(G,'XData',stopsLon,'YData',stopsLat,'LineStyle','none','NodeLabel',{});
hold on
% Draw the outside border
plot(x,y,'r-')
hold off

tsp = optimproblem;
trips = optimvar('trips',lendist,1,'Type','integer','LowerBound',0,'UpperBound',1);

tsp.Objective = dist'*trips;

% outedges = Gibt alle IDs der Verbindungen aus, die von dem "Stop/Punkt"
% ausgehen
% optimconstr = Erstellt ein Leeres Array mit 200 Feldern für den
% Constraint. Die 1 gibt an, dass ein Parameter (an welchem Punkt) mitgeschickt werden soll,
% wenn ein Constraint an einer stelle im Array hinzugefügt werden soll.
constr2trips = optimconstr(nStops,1);
for stop = 1:nStops
    whichIdxs = outedges(G,stop); % Identify trips associated with the stop
    constr2trips(stop) = sum(trips(whichIdxs)) == 2;
end
tsp.Constraints.constr2trips = constr2trips;

opts = optimoptions('intlinprog','Display','off');
tspsol = solve(tsp,'options',opts);

tspsol.trips = logical(round(tspsol.trips));
% Gsol = graph(idxs(tspsol.trips,1),idxs(tspsol.trips,2),[],numnodes(G));
Gsol = graph(idxs(tspsol.trips,1),idxs(tspsol.trips,2)); % Also works in most cases

hold on
highlight(hGraph,Gsol,'LineStyle','-')
title('Solution with Subtours')

% conncomp schaut sich die Verbindungen und Punkt an und gibt an zu welcher
% Subtour der jeweilige Punkt gehört. Beispiel: Der 1. Subtour geht durch
% Punkt 1, Punkt 2 und Punkt 3 --> ConnComp gibt dann folgendes aus: 1 1 1
% da alle 3 Punkte zur 1. Subtour gehören
% max(tourIdxs) liefert daraus folgend die Anzahl der Subtouren, da die
% höchte Zahl im Array die letzte Subtour repräsentiert.
tourIdxs = conncomp(Gsol);
numtours = max(tourIdxs); % Number of subtours
fprintf('# of subtours: %d\n',numtours);

% Diese Schleife beginnt damit, dass solange numtours größer als 1 ist die
% Schleife weiterläuft. 

% Als nächstes wird durch alle Numtours (Anzahl aller Subtouren) iteriert.
% Dabei wird in jeder Iteration die Variable "inSubTour" ob die gerade
% betrachtete Verbindung zu der zu prüfenden Subtour gehört. Die Variable
% "inSubTour" kann man dabei wie ein Array betrachten, welches So viele
% Stellen hat wie es Verbindungen gibt. 

% Befindet sich nun die Verbindung in der gerade betrachteten Subtour so
% wird der Wert im Array "inSubTour" für diese Verbindung auf 1 gesetzt.

% Mit dem a = all(...) Befehl erstellen wir ein Array welches für die Stellen,
% wo keine 0 Steht eine 1 zurück gibt und für alle Stellen wo die Werte 0
% sind eine 0 zurück gibt.
% Nun haben wir sozusagen ein Array, welches für alle Verbindungen 0 hat
% außer die Verbindungen die zur gerade relevanten Subtour gehört. Diese
% haben den Wert 1.

% Mit a können wir nun für diese eine Subtour die Nebenbedingung hinzufügen, dass die Summe der
% Verbindungen mit dem Wert 1 <= die Summe der Verbindungen mit dem Wert 1
% in der gerade betrachteten Subtour - 1 ist.

% Dies Funktioniert, weil beispielsweise zu einer Subtour mit 3 Punkten 3
% Verbindungen gehören. Stellt man nun unsere Nebenbedinungen dazu auf dann
% kann es höchstens 2 Verbindungen geben und somit keine Subtour entstehen.

% Index of added constraints for subtours
k = 1;
while numtours > 1 % Repeat until there is just one subtour
    % Add the subtour constraints
    for ii = 1:numtours
        inSubTour = (tourIdxs == ii); % Edges in current subtour
        a = all(inSubTour(idxs),2); % Complete graph indices with both ends in subtour
        constrname = "subtourconstr" + num2str(k);
        tsp.Constraints.(constrname) = sum(trips(a)) <= (nnz(inSubTour) - 1);
        k = k + 1;        
    end
    
    % Try to optimize again
    [tspsol,fval,exitflag,output] = solve(tsp,'options',opts);
    tspsol.trips = logical(round(tspsol.trips));
    Gsol = graph(idxs(tspsol.trips,1),idxs(tspsol.trips,2),[],numnodes(G));
    % Gsol = graph(idxs(tspsol.trips,1),idxs(tspsol.trips,2)); % Also works in most cases
    
    % Plot new solution
    hGraph.LineStyle = 'none'; % Remove the previous highlighted path
    highlight(hGraph,Gsol,'LineStyle','-')
    drawnow

    % How many subtours this time?
    tourIdxs = conncomp(Gsol);
    numtours = max(tourIdxs); % Number of subtours
    fprintf('# of subtours: %d\n',numtours)    
end