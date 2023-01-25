import sys

if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'env' :
        import coproximity_create_vocabulary.generate_env
    else :
        raise Exception(f'main action unknown, is: {action} , should be in {["env"]}')
