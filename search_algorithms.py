from heapq import heappush, heappop
from collections import deque
from math import sqrt
import pygame
import time
import sys


class Node:
	def __init__(self, state, parent, cost = 0.0, heuristic = 0.0):
		self.state = state
		self.parent = parent
		self.cost = cost
		self.heuristic = heuristic

	def __lt__(self, other):
		return (self.cost + self.heuristic) < (other.cost + other.heuristic)


class GreedyNode:
	def __init__(self, state, parent, heuristic = 0.0):
		self.state = state
		self.parent = parent
		self.heuristic = heuristic

	def __lt__(self, other):
		return self.heuristic < other.heuristic


class DijkstraNode:
	def __init__(self, state, parent, cost = 0.0):
		self.state = state
		self.parent = parent
		self.cost = cost

	def __lt__(self, other):
		return self.cost < other.cost


def dfs(draw_search, maze):
	result_path = []
	size = 0

	frontier = deque()
	frontier.append(Node(maze.start, None))
	explored = {maze.start, }

	while frontier:
		size += 1
		current_node  = frontier.pop()
		current_state = current_node.state

		if maze.goal_test(current_state):
			result_path.append(node_to_path(current_node, size))
			
			if not maze.goals:
				return result_path

			size = 0
			frontier = deque()
			frontier.append(Node(maze.start, None))
			explored = {maze.start, }

		else:
			for child in maze.successors(current_state):
				if child in explored:
					continue

				explored.add(child)
				frontier.append(Node(child, current_node))

		draw_search(current_state, maze.visited, maze.start)

	return None


def bfs(draw_search, maze):
	result_path = []
	size = 0

	frontier = deque()
	frontier.append(Node(maze.start, None))
	explored = {maze.start, }

	while frontier:
		size += 1
		current_node  = frontier.popleft()
		current_state = current_node.state

		if maze.goal_test(current_state):
			result_path.append(node_to_path(current_node, size))

			if not maze.goals:
				return result_path

			size = 0
			frontier = deque()
			frontier.append(Node(maze.start, None))
			explored = {maze.start, }

		else:
			for child in maze.successors(current_state):
				if child in explored:
					continue

				explored.add(child)
				frontier.append(Node(child, current_node))

		draw_search(current_state, maze.visited, maze.start)

	return None


def astar(draw_search, maze, distance_function):
	result_path = []
	size = 0

	heuristic = distance_function(maze.goals, maze.start, maze.ordered_search)

	frontier = []
	heappush(frontier, Node(maze.start, None, 0.0, heuristic(maze.start)))
	explored = {maze.start: 0.0, }

	while frontier:
		size += 1
		current_node  = heappop(frontier)
		current_state = current_node.state

		if maze.goal_test(current_state):
			result_path.append(node_to_path(current_node, size))

			if not maze.goals:
				return result_path

			size = 0
			heuristic = distance_function(maze.goals, maze.start, maze.ordered_search)

			frontier = []
			heappush(frontier, Node(maze.start, None, 0.0, heuristic(maze.start)))
			explored = {maze.start: 0.0, }

		else:
			for child in maze.successors(current_state):
				new_cost = current_node.cost + 1

				if child not in explored or explored[child] > new_cost:
					explored[child] = new_cost
					heappush(frontier, Node(child, current_node, new_cost, heuristic(child)))

		draw_search(current_state, maze.visited, maze.start)

	return None


def greedy(draw_search, maze, distance_function):
	result_path = []
	size = 0

	heuristic = distance_function(maze.goals, maze.start, maze.ordered_search)

	frontier = []
	heappush(frontier, GreedyNode(maze.start, None, heuristic(maze.start)))
	explored = {maze.start, }

	while frontier:
		size += 1
		current_node  = heappop(frontier)
		current_state = current_node.state

		if maze.goal_test(current_state):
			result_path.append(node_to_path(current_node, size))

			if not maze.goals:
				return result_path

			size = 0
			heuristic = distance_function(maze.goals, maze.start, maze.ordered_search)

			frontier = []
			heappush(frontier, GreedyNode(maze.start, None, heuristic(maze.start)))
			explored = {maze.start, }

		else:
			for child in maze.successors(current_state):
				if child in explored:
					continue

				explored.add(child)
				heappush(frontier, GreedyNode(child, current_node, heuristic(child)))

		draw_search(current_state, maze.visited, maze.start)

	return None


def dijkstra(draw_search, maze):
	result_path = []
	size = 0

	frontier = []
	heappush(frontier, DijkstraNode(maze.start, None, 0.0))
	explored = {maze.start: 0.0, }

	while frontier:
		size += 1
		current_node = heappop(frontier)
		current_state = current_node.state

		if maze.goal_test(current_state):
			result_path.append(node_to_path(current_node, size))

			if not maze.goals:
				return result_path

			size = 0
			frontier = []
			heappush(frontier, DijkstraNode(maze.start, None, 0.0))
			explored = {maze.start: 0.0, }

		else:
			for child in maze.successors(current_state):
				new_cost = current_node.cost + 1

				if child not in explored or explored[child] > new_cost:
					explored[child] = new_cost
					heappush(frontier, Node(child, current_node, new_cost))

		draw_search(current_state, maze.visited, maze.start)

	return None

			
def node_to_path(node, explored_size):
	path = [node.state]

	while node.parent is not None:
		node = node.parent
		path.append(node.state)

	path.reverse()
	return (len(path), explored_size, path)


def manhattan_distance(goals, start, order):

	i_goal = 0
	if not order:
		h = manhattan(start)
		dist = float('inf')
		for i, goal in enumerate(goals):
			cur_dist = h(goal)
			if cur_dist < dist:
				dist = cur_dist
				i_goal = i

	return manhattan(goals[i_goal])


def manhattan(goal):
	def distance(pos):
		x_dist = abs(pos[1] - goal[1])
		y_dist = abs(pos[0] - goal[0])
		return x_dist + y_dist
	return distance


def euclidean_distance(goals, start, order):

	i_goal = 0
	if not order:
		h = euclidean(start)
		dist = float('inf')
		for i, goal in enumerate(goals):
			cur_dist = h(goal)
			if cur_dist < dist:
				dist = cur_dist
				i_goal = i

	return euclidean(goals[i_goal])


def euclidean(goal):
	def distance(pos):
		x_dist = pos[1] - goal[1]
		y_dist = pos[0] - goal[0]
		return sqrt((x_dist * x_dist) + (y_dist * y_dist))
	return distance


def init_algorithm(algorithm, heuristic, maze, draw_search):

	path = None

	if heuristic == 'manhattan':
		distance_function = manhattan_distance
	else:
		distance_function = euclidean_distance

	if algorithm == 'BFS':
		path = bfs(draw_search, maze)
	elif algorithm == 'DFS':
		path = dfs(draw_search, maze)
	elif algorithm == 'A*':
		path = astar(draw_search, maze, distance_function)
	elif algorithm == 'Greedy':
		path = greedy(draw_search, maze, distance_function)
	elif algorithm == 'Dijkstra':
		path = dijkstra(draw_search, maze)
	else:
		path = None

	return path
