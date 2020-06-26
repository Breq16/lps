import numpy as np


def get_matrices(corners, size):
    def map_basis_to_points(points):
        homo_points = [np.array([[point[0]], [point[1]], [1]])
                       for point in points]

        three_points = np.concatenate(homo_points[:3], axis=1)

        coefficients = np.matmul(np.linalg.inv(three_points), homo_points[3])

        scaled = np.matmul(three_points,
                           np.array([[coefficients[0][0], 0, 0],
                                     [0, coefficients[1][0], 0],
                                     [0, 0, coefficients[2][0]]]))
        return scaled

    scene_corners = ((size/2, size/2), (-size/2, size/2),
                     (-size/2, -size/2), (size/2, -size/2))

    basis_to_pic = map_basis_to_points(corners)
    basis_to_scene = map_basis_to_points(scene_corners)

    pic_to_scene = np.matmul(basis_to_scene, np.linalg.inv(basis_to_pic))
    scene_to_pic = np.matmul(basis_to_pic, np.linalg.inv(basis_to_scene))

    pic_to_scene /= pic_to_scene[2][2]
    scene_to_pic /= scene_to_pic[2][2]

    return pic_to_scene, scene_to_pic


def apply(source_point, matrix):
    homo_source_point = np.array([[coord] for coord in source_point] + [[1]])
    homo_dest_point = np.matmul(matrix, homo_source_point)
    dest_point = (homo_dest_point[0][0] / homo_dest_point[2][0],
                  homo_dest_point[1][0] / homo_dest_point[2][0])
    return dest_point
