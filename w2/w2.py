def calculate_z_array(S):
    Z = [0 for i in range(0, len(S))]
    L = R = 0
    Z[0] = 0  # pre-initalise the z-value of the first character as 0

    for K in range(1, len(S) - 1):

        ## If k > r, then cannot infer values
        if K > R:
            L = R = K  # initialise a new z-box
            while R < len(S) and S[R] == S[R - L]:
                # while no mismatch, keep expanding z-box
                R += 1
            Z[K] = R - L  # z-value will be the size of the z box
            R -= 1

        ## If k > r, then can infer values
        else:  # K >= R
            kp = K - L + 1  # take the mirrored value
            dist = R - K  # take the distance between k and right threshold

            # Using previously calculated values
            if Z[kp] < dist:
                Z[K] = Z[kp]

            # Y != Z, prefix match truncates at R-L
            if Z[kp] > dist:
                Z[K] = dist

            # Z[kp] = dist # Y ? Z, must perform more matches
            else:
                L = R = K  # initialize A NEW Z -BOX
                while (
                    R < len(S) and S[R] == S[R - L]
                ):  # while no mismatch, keep expanding z-box
                    R += 1
                Z[K] = R - L  # z-value will be the size of the z box
                R -= 1

    return Z
