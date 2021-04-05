from collections import deque as queue

# graph is in adjacent list representation


def bfs(graph, start, end):
    # maintain a queue of paths
    queue = []
    # push the first path into the queue
    queue.append([start])
    while queue:
        # get the first path from the queue
        print(queue)

        path = queue.pop(0)
        # get the last node from the path
        node = path[-1]
        # path found
        if node == end:
            return path
        # enumerate all adjacent nodes, construct a new path and push it into the queue
        for adjacent in graph.get(node, []):
            new_path = list(path)
            new_path.append(adjacent)
            queue.append(new_path)


# Direction vectors
dRow = [-1, 0, 1, 0]
dCol = [0, 1, 0, -1]
# Function to check if a cell
# is be visited or not


def isValid(vis, row, col):

    # If cell lies out of bounds
    if (row < 0 or col < 0 or row >= 4 or col >= 4):
        return False

    # If cell is already visited
    if (vis[row][col]):
        return False

    # Otherwise
    return True

# Function to perform the BFS traversal


def bfs_ver2(grid, vis, row, col, end):

    # Stores indices of the matrix cells
    q = queue()

    # Mark the starting cell as visited
    # and push it into the queue
    q.append([(row, col)])
    vis[row][col] = True

    # Iterate while the queue
    # is not empty
    while (len(q) > 0):
        path = q.popleft()

        # get the last node from the path
        node = path[-1]
        if node == end:
            return path

        # Go to the adjacent cells
        for i in range(4):
            adjx = node[0] + dRow[i]
            adjy = node[1] + dCol[i]
            if (isValid(vis, adjx, adjy)):
                new_path = list(path)
                new_path.append((adjx, adjy))
                q.append(new_path)
                vis[adjx][adjy] = True


if __name__ == "__main__":

    # method 1
    graph = {
        '1': ['2', '3', '4'],
        '2': ['5', '6'],
        '5': ['9', '10'],
        '4': ['7', '8'],
        '7': ['11', '12']
    }
    # print(bfs(graph, '1', '11'))

    # Method 2
    grid = [[1, 2, 3, 4],
            [5, 6, 7, 8],
            [9, 10, 11, 12],
            [13, 14, 15, 16]]

    # Declare the visited array
    vis = [[False for i in range(4)] for i in range(4)]
    # vis, False, sizeof vis)

    res = bfs_ver2(grid, vis, 0, 0, (3, 3))
    print(res)
