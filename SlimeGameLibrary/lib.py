import json
import math
import numbers
import random
from collections import deque
from typing import Literal

from .data import colors, outputs, ports, sizes
from .utils import Color, Vector2, Vector3, generateId

data = {"serializableNodes": [], "serializableConnections": []}


class Node:
    def __init__(self, data: dict, outputIndex=1):
        self.data = data
        self.outputIndex = outputIndex
        self.type = outputs[data["id"]]
        self.inputPorts = {}
        self.outputPorts = {}
        for port in data["serializablePorts"]:
            if port["polarity"] == 0:
                self.inputPorts[port["id"]] = port
            else:
                self.outputPorts[port["id"]] = port

    def __repr__(self):
        return f"Node(type='{self.type}', id='{self.data.get('sID', 'unknown')}')"

    def __add__(self, other):
        if isinstance(other, Node):
            from .nodes import AddFloats, AddVector3

            if self.type == float and other.type == float:
                return AddFloats(self, other)
            if self.type == "Vector3" and other.type == "Vector3":
                return AddVector3(self, other)
        elif isinstance(other, numbers.Number) and self.type == float:
            from .nodes import AddFloats, Float

            return AddFloats(self, Float(other))

        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Node):
            from .nodes import SubtractFloats, SubtractVector3

            if self.type == float and other.type == float:
                return SubtractFloats(self, other)
            if self.type == "Vector3" and other.type == "Vector3":
                return SubtractVector3(self, other)
        elif isinstance(other, numbers.Number) and self.type == float:
            from .nodes import Float, SubtractFloats

            return SubtractFloats(self, Float(other))

        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, numbers.Number) and self.type == float:
            from .nodes import Float, SubtractFloats

            return SubtractFloats(Float(other), self)

        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, Node):
            from .nodes import MultiplyFloats, ScaleVector3

            if self.type == float and other.type == float:
                return MultiplyFloats(self, other)
            if self.type == "Vector3" and other.type == float:
                return ScaleVector3(self, other)
        elif isinstance(other, numbers.Number) and self.type == float:
            from .nodes import Float, MultiplyFloats

            return MultiplyFloats(self, Float(other))

        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, Node):
            from .nodes import DivideFloats

            if self.type == float and other.type == float:
                return DivideFloats(self, other)
        elif isinstance(other, numbers.Number) and self.type == float:
            from .nodes import DivideFloats, Float

            return DivideFloats(self, Float(other))

        return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, numbers.Number) and self.type == float:
            from .nodes import DivideFloats, Float

            return DivideFloats(Float(other), self)

        return NotImplemented

    def __floordiv__(self, other):
        result = self.__truediv__(other)
        if result is NotImplemented:
            return result
        from .nodes import Operation

        return Operation(result, "floor")

    def __rfloordiv__(self, other):
        if isinstance(other, numbers.Number) and self.type == float:
            from .nodes import DivideFloats, Float, Operation

            result = DivideFloats(Float(other), self)
            return Operation(result, "floor")

        return NotImplemented

    def __mod__(self, other):
        if isinstance(other, Node):
            from .nodes import Modulo

            if self.type == float and other.type == float:
                return Modulo(self, other)
        elif isinstance(other, numbers.Number) and self.type == float:
            from .nodes import Float, Modulo

            return Modulo(self, Float(other))

        return NotImplemented

    def __rmod__(self, other):
        if isinstance(other, numbers.Number) and self.type == float:
            from .nodes import Float, Modulo

            return Modulo(Float(other), self)

        return NotImplemented

    def __pow__(self, other):
        if isinstance(other, Node):
            from .nodes import Power

            if self.type == float and other.type == float:
                return Power(self, other)
        elif isinstance(other, numbers.Number) and self.type == float:
            from .nodes import Power

            return Power(self, other)

        return NotImplemented

    def __rpow__(self, other):
        if isinstance(other, numbers.Number) and self.type == float:
            from .nodes import Power

            return Power(self, other)

        return NotImplemented

    def __neg__(self):
        from .nodes import Float, MultiplyFloats

        if self.type == float:
            return MultiplyFloats(self, Float(-1))

        return NotImplemented

    def __pos__(self):
        return self

    def __abs__(self):
        from .nodes import Operation

        if self.type == float:
            return Operation(self, "abs")

        return NotImplemented

    def __invert__(self):
        from .nodes import Not

        if self.type == bool:
            return Not(self)

        return NotImplemented

    def __eq__(self, other):
        from .nodes import CompareBool, CompareFloats, Float

        if isinstance(other, Node):
            if self.type == float and other.type == float:
                return CompareFloats(self, other)
            if self.type == bool and other.type == bool:
                return CompareBool(self, other)

        elif isinstance(other, numbers.Number) and self.type == float:
            return CompareFloats(self, Float(other))

        elif isinstance(other, bool) and self.type == bool:
            from .nodes import Bool

            return CompareBool(self, Bool(other))

        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        from .nodes import Not

        return Not(result)

    def __lt__(self, other):
        if isinstance(other, Node):
            from .nodes import CompareFloats

            if self.type == float and other.type == float:
                return CompareFloats(self, other, "<")
        elif isinstance(other, numbers.Number) and self.type == float:
            from .nodes import CompareFloats, Float

            return CompareFloats(self, Float(other), "<")

        return NotImplemented

    def __le__(self, other):
        if isinstance(other, Node):
            from .nodes import CompareFloats

            if self.type == float and other.type == float:
                return CompareFloats(self, other, "<=")
        elif isinstance(other, numbers.Number) and self.type == float:
            from .nodes import CompareFloats, Float

            return CompareFloats(self, Float(other), "<=")

        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Node):
            from .nodes import CompareFloats

            if self.type == float and other.type == float:
                return CompareFloats(self, other, ">")
        elif isinstance(other, numbers.Number) and self.type == float:
            from .nodes import CompareFloats, Float

            return CompareFloats(self, Float(other), ">")

        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, Node):
            from .nodes import CompareFloats

            if self.type == float and other.type == float:
                return CompareFloats(self, other, ">=")
        elif isinstance(other, numbers.Number) and self.type == float:
            from .nodes import CompareFloats, Float

            return CompareFloats(self, Float(other), ">=")

        return NotImplemented

    def __and__(self, other):
        if isinstance(other, Node):
            from .nodes import CompareBool

            if self.type == bool and other.type == bool:
                return CompareBool(self, other, "and")
        elif isinstance(other, bool) and self.type == bool:
            from .nodes import Bool, CompareBool

            return CompareBool(self, Bool(other), "and")

        return NotImplemented

    def __rand__(self, other):
        if isinstance(other, bool) and self.type == bool:
            from .nodes import Bool, CompareBool

            return CompareBool(Bool(other), self, "and")

        return NotImplemented

    def __or__(self, other):
        if isinstance(other, Node):
            from .nodes import CompareBool

            if self.type == bool and other.type == bool:
                return CompareBool(self, other, "or")
        elif isinstance(other, bool) and self.type == bool:
            from .nodes import Bool, CompareBool

            return CompareBool(self, Bool(other), "or")

        return NotImplemented

    def __ror__(self, other):
        if isinstance(other, bool) and self.type == bool:
            from .nodes import Bool, CompareBool

            return CompareBool(Bool(other), self, "or")

        return NotImplemented

    def __xor__(self, other):
        if isinstance(other, Node):
            from .nodes import CompareBool

            if self.type == bool and other.type == bool:
                return CompareBool(self, other, "xor")
        elif isinstance(other, bool) and self.type == bool:
            from .nodes import Bool, CompareBool

            return CompareBool(self, Bool(other), "xor")

        return NotImplemented

    def __rxor__(self, other):
        if isinstance(other, bool) and self.type == bool:
            from .nodes import Bool, CompareBool

            return CompareBool(Bool(other), self, "xor")

        return NotImplemented

    def __matmul__(self, other):
        if isinstance(other, Node):
            from .nodes import DotProduct

            if self.type == "Vector3" and other.type == "Vector3":
                return DotProduct(self, other)

        return NotImplemented

    def __rmatmul__(self, other):
        return self.__matmul__(other)


def AddNode(nodeName, nodeValue="", includePorts=True, position=None):
    node = {}

    if position is None:
        position = Vector3(0, 0)

    nodeId = generateId()
    instanceId = random.randint(0, 999999)

    node["serializableRectTransform"] = {}
    node["serializableRectTransform"]["position"] = Vector3(0, 0)
    node["serializableRectTransform"]["localPosition"] = position
    node["serializableRectTransform"]["anchorMin"] = Vector2(0, 1)
    node["serializableRectTransform"]["anchorMax"] = Vector2(0, 1)
    node["serializableRectTransform"]["sizeDelta"] = sizes[nodeName]
    node["serializableRectTransform"]["scale"] = Vector3(1, 1, 1)
    node["id"] = nodeName
    node["sID"] = nodeId
    node["enableSelfConnection"] = False
    node["enableDrag"] = True
    node["enableHover"] = False
    node["enableSelect"] = True
    node["disableClick"] = False
    node["modifier"] = nodeValue
    node["defaultColor"] = colors[nodeName]
    node["outlineSelectedColor"] = Color(1, 0.58, 0.04)
    node["outlineHoverColor"] = Color(1, 0.81, 0.3)
    node["serializablePorts"] = []
    if includePorts:
        for portData in ports[nodeName]:
            node["serializablePorts"].append(
                {
                    "serializableRectTransform": {
                        "position": Vector3(0, 0),
                        "localPosition": portData["position"],
                        "anchorMin": Vector2(0, 1),
                        "anchorMax": Vector2(0, 1),
                        "sizeDelta": Vector2(40, 40),
                        "scale": Vector3(1, 1, 1),
                    },
                    "id": portData["id"],
                    "sID": generateId(),
                    "polarity": portData["polarity"],
                    "maxConnections": portData["maxConnections"],
                    "iconColorDefault": portData["iconColorDefault"],
                    "iconColorHover": portData["iconColorHover"],
                    "iconColorSelected": portData["iconColorSelected"],
                    "iconColorConnected": Color(1, 1, 1),
                    "enableDrag": True,
                    "enableHover": True,
                    "disableClick": False,
                    "controlPointSerializableRectTransform": {
                        "position": Vector3(0, 0),
                        "localPosition": portData["controlPointPosition"],
                        "anchorMin": Vector2(0.5, 0.5),
                        "anchorMax": Vector2(0.5, 0.5),
                        "sizeDelta": Vector2(0, 0),
                        "scale": Vector3(2.21, 2.21, 2.21),
                    },
                    "nodeInstanceID": instanceId,
                    "nodeSID": nodeId,
                }
            )

    data["serializableNodes"].append(node)

    return Node(node)


def ConnectPorts(portType: tuple | str, node0: Node, node1: Node):
    if isinstance(portType, tuple):
        port0 = node0.outputPorts[portType[0]]
        port1 = node1.inputPorts[portType[1]]
    else:
        port0 = node0.outputPorts[portType]
        port1 = node1.inputPorts[portType]
    connection = {}
    connection["id"] = f"Connection ({port0["id"]} - {port1["id"]})"
    connection["sID"] = generateId()
    connection["port0InstanceID"] = port0["nodeInstanceID"]
    connection["port1InstanceID"] = port1["nodeInstanceID"]
    connection["port0SID"] = port0["sID"]
    connection["port1SID"] = port1["sID"]
    connection["selectedColor"] = Color(1.0, 0.58, 0.04)
    connection["hoverColor"] = Color(1.0, 0.81, 0.3)
    connection["defaultColor"] = Color(0.98, 0.94, 0.84)
    connection["curveStyle"] = 2
    connection["label"] = ""
    connection["line"] = {
        "capStart": {
            "active": False,
            "shape": 3,
            "size": 5.0,
            "color": Color(1.0, 0.81, 0.3),
            "angleOffset": 0.0,
        },
        "capEnd": {
            "active": False,
            "shape": 3,
            "size": 5.0,
            "color": Color(1.0, 0.81, 0.3),
            "angleOffset": 0.0,
        },
        "ID": "",
        "startWidth": 3.0,
        "endWidth": 3.0,
        "dashDistance": 5.0,
        "color": Color(0.98, 0.94, 0.84),
        "points": [
            port0["serializableRectTransform"]["localPosition"],
            port0["controlPointSerializableRectTransform"]["localPosition"],
            port1["serializableRectTransform"]["localPosition"],
            port1["controlPointSerializableRectTransform"]["localPosition"],
        ],
        "lineStyle": 0,
        "length": 0,
        "animation": {
            "isActive": False,
            "pointsDistance": 90.0,
            "size": 10.0,
            "color": port0["iconColorDefault"],
            "shape": 1,
            "speed": 0.0,
        },
    }
    connection["enableDrag"] = True
    connection["enableHover"] = True
    connection["enableSelect"] = True
    connection["disableClick"] = False

    data["serializableConnections"].append(connection)
    return connection


def findNodeByPortSID(portSID):
    for node in data["serializableNodes"]:
        for port in node["serializablePorts"]:
            if port["sID"] == portSID:
                return node
    return None


def gridLayout(offsetX=350, offsetY=-215):
    x = 1263
    y = -278
    nodesPerRow = max(1, int(math.sqrt(len(data["serializableNodes"]))))

    for i, node in enumerate(data["serializableNodes"]):
        transform = node["serializableRectTransform"]
        if transform["localPosition"] != Vector3(0, 0):
            continue
        transform["localPosition"] = Vector3(x, y)
        x += offsetX
        if (i + 1) % nodesPerRow == 0:
            x = 1263
            y += offsetY


def autoLayout(offsetX=350, offsetY=-215):
    adj = {}
    inDegree = {}

    for node in data["serializableNodes"]:
        adj[node["sID"]] = []
        inDegree[node["sID"]] = 0

    for conn in data["serializableConnections"]:
        sourceNode = findNodeByPortSID(conn["port0SID"])
        destNode = findNodeByPortSID(conn["port1SID"])

        if sourceNode and destNode and sourceNode["sID"] != destNode["sID"]:
            adj[sourceNode["sID"]].append(destNode["sID"])
            inDegree[destNode["sID"]] += 1

    queue = deque()
    for nodeSID, degree in inDegree.items():
        if degree == 0:
            queue.append(nodeSID)

    nodeRegistry = {node["sID"]: node for node in data["serializableNodes"]}

    nodeLevels = {nodeSID: 0 for nodeSID in nodeRegistry.keys()}
    visitedCount = 0

    while queue:
        u = queue.popleft()
        visitedCount += 1

        for v in adj[u]:
            nodeLevels[v] = max(nodeLevels[v], nodeLevels[u] + 1)
            inDegree[v] -= 1
            if inDegree[v] == 0:
                queue.append(v)

    if visitedCount < len(data["serializableNodes"]):
        gridLayout(offsetX, offsetY)
        return

    columns = {}
    for nodeSID, level in nodeLevels.items():
        if level not in columns:
            columns[level] = []
        columns[level].append(nodeRegistry[nodeSID])

    sortedColumns = sorted(columns.items())

    currentX = 1263
    for level, nodesInColumn in sortedColumns:
        totalHeight = (len(nodesInColumn) - 1) * offsetY
        currentY = -totalHeight / 2.0 - 278

        for node in nodesInColumn:
            transform = node["serializableRectTransform"]
            if transform["localPosition"] != Vector3(0, 0):
                continue
            transform["localPosition"] = Vector3(currentX, currentY)
            currentY += offsetY

        currentX += offsetX


def updateConnectionLinePoints():
    for connection in data["serializableConnections"]:
        port0 = None
        port1 = None

        for node in data["serializableNodes"]:
            for port in node["serializablePorts"]:
                if port["sID"] == connection["port0SID"]:
                    port0 = port
                elif port["sID"] == connection["port1SID"]:
                    port1 = port

        if port0 and port1:
            connection["line"]["points"] = [
                port0["serializableRectTransform"]["localPosition"],
                port0["controlPointSerializableRectTransform"]["localPosition"],
                port1["serializableRectTransform"]["localPosition"],
                port1["controlPointSerializableRectTransform"]["localPosition"],
            ]


def removeUnusedNodes():
    connectedPortSIDs = set()
    for connection in data["serializableConnections"]:
        connectedPortSIDs.add(connection["port0SID"])
        connectedPortSIDs.add(connection["port1SID"])

    nodesToRemove = []
    for node in data["serializableNodes"].copy():
        if node["serializableRectTransform"]["localPosition"] != Vector3(0, 0):
            continue  # skips Debug nodes cuz they have "unused node" String attached

        nodeHasConnections = False
        for port in node["serializablePorts"]:
            if port["sID"] in connectedPortSIDs:
                nodeHasConnections = True
                break

        if not nodeHasConnections:
            data["serializableNodes"].remove(node)

    return len(nodesToRemove)


def SaveData(
    filePath,
    layout: Literal["auto", "grid", "single", "hidden", None] = "auto",
    pruneUnusedNodes=True,
    keepPosition=True,
):
    if pruneUnusedNodes:
        removeUnusedNodes()

    match layout:
        case "auto":
            autoLayout()
        case "grid":
            gridLayout()
        case "single":
            for node in data["serializableNodes"]:
                transform = node["serializableRectTransform"]
                if transform["localPosition"] != Vector3(0, 0) and keepPosition:
                    continue
                transform["localPosition"] = Vector3(0, 0)
        case "hidden":
            for node in data["serializableNodes"]:
                transform = node["serializableRectTransform"]
                if transform["localPosition"] != Vector3(0, 0) and keepPosition:
                    continue
                transform["localPosition"] = Vector3(9999, 9999)
                transform["scale"] = Vector3(0, 0)

    updateConnectionLinePoints()

    with open(filePath, "w") as f:
        json.dump(data, f, separators=(",", ":"))
