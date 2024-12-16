import multiprocessing.connection
import sys
import os
import ollama
import typing
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
if typing.TYPE_CHECKING:
    from requirement_tree.requirement_tree import RequirementTree
from requirement_tree.requirement_tree_visitor import BackgroundCodeGenerateVisitor

def generate_code(conn: multiprocessing.connection.Connection, tree: 'RequirementTree'):
    return
    print('start generate code at background')
    visitor = BackgroundCodeGenerateVisitor(conn)
    tree.root.accept(visitor)
    print('finish generate code at background')
    try:
        conn.send(tree)
        print('sent')
    except BrokenPipeError:
        print('broken pipe')
        pass
    conn.close()


