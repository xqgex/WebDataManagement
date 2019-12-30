import sys
import numpy as np

FILE_OUTPUT = "./question1c.txt"


def save(indices, pagerank):
    with open(FILE_OUTPUT, 'a+') as outfile:
        outfile.write('\n\nSection b:\n')
        for site, index in indices.iteritems():
            outfile.write("{}: {}\n".format(site, pagerank[index]))


def initAdjacencyMatrix(sites, indices):
    '''
    Initialize graph as an adjancy matrix
    '''
    N = len(sites)
    sites_graph = np.zeros((N, N))
    for site, links in sites.iteritems():
        P = len(links)
        i = indices[site]
        for link in links:
            sites_graph[i, indices[link]] = 1.0 / P

    return sites_graph.transpose()


def parseGraph(input_file):
    '''
    Parse graph from text file
    '''
    with open(input_file, 'r') as infile:
        sites   = {}
        indices = {}
        i = 0
        for line in infile:
            line_parts = line.split("=")
            site = line_parts[0].strip()
            parts = line_parts[1]
            tmp = parts[parts.find("{")+1:parts.find("}")]  # Get sites inside curly brackets
            site_links = tmp.split(", ") if len(tmp) > 0 else [site]  # Split by ','; if empty --> add self-loop
            sites[site]     = site_links
            indices[site]   = i
            i += 1

    return initAdjacencyMatrix(sites, indices), indices


def pageRank(adj_mat, indices, damping_factor=0.3, iters=100, epsilon=10**-10, to_save=False):
    N = adj_mat.shape[0]
    curr_pagerank_vec = np.array([1.0/N] * N)  # Start with uniform distribution
    M = (damping_factor / N) * np.ones((N, N)) + (1 - damping_factor) * adj_mat  # Pagerank matrix
    for i in range(iters):
        prev_pagerank_vec = curr_pagerank_vec.copy()
        curr_pagerank_vec = np.dot(M, curr_pagerank_vec)
        if np.linalg.norm(curr_pagerank_vec - prev_pagerank_vec) <= epsilon:  # If converged (up to epsilon)
            break

    if to_save:  # Save results to file
        save(indices, curr_pagerank_vec)

    # Print results to screen
    for site, index in sorted(indices.iteritems()):
        print "{}: {}".format(site, curr_pagerank_vec[index])


def main(data_file):
    '''
    :param data_file: text file with sites and links as they are printed in question 1a
    '''
    adj_mat, indices = parseGraph(data_file)  # initialize graph adjacency matrix
    pageRank(adj_mat, indices, to_save=True)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Invalid call"
    else:
        main(sys.argv[1])
