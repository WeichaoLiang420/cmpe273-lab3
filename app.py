from ariadne import QueryType, graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, MutationType
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify

student_id = 1001
class_id = 2001
students = {}

classes = {}

type_defs = """
    type Query {
      hello: String!
      StudentInfo(student_id: ID!): Student!
      ClassInfo(class_id: ID!): cClass!
     }

    type Mutation {
      NewStudent(student_name: String!): Student!
      NewClass(class_name: String!): cClass!
      addStudent(student_id: ID!, class_id: ID!): cClass
    }

    type Student {
      student_id: ID!
      student_name: String!
    }

    type cClass {
        class_id: ID!
        class_name: String!
        students: [Student!]!
    }
"""
query = QueryType()
mutation = MutationType()


@mutation.field("NewStudent")
def NewStudent(_, info, student_name):
    global student_id
    student_id += 1
    students[student_id] = student_name
    return {'student_id': student_id, 'student_name': student_name}

@query.field("StudentInfo")
def StudentInfo(_, info, student_id):
    print(students)
    return {'student_id': student_id, 'student_name': students.get(int(student_id))}

@mutation.field("NewClass")
def NewClass(_, info, class_name):
    global class_id
    class_id += 1
    classes[class_id] = { 'class_name': class_name, 'students': [] }
    return {'class_id': class_id, 'class_name': class_name, 'students': []}

@query.field("ClassInfo")
def ClassInfo(_, info, class_id):
    temp=classes.get(int(class_id))
    return {'class_id': class_id, 'class_name': temp['class_name'], 'students': temp['students']}

@mutation.field("addStudent")
def addStudent(_, info, student_id, class_id):
    print(students)
    student_name=students[int(student_id)]
    classes[int(class_id)]['students'].append( {'student_id' : student_id, 'student_name': student_name} )
    temp = classes.get(int(class_id))
    return {'class_id': class_id, 'class_name': temp['class_name'], 'students': temp['students']}

schema = make_executable_schema(type_defs, [query, mutation])
app = Flask(__name__)


@app.route("/graphql", methods=["GET"])
def graphql_playgroud():
    # On GET request serve GraphQL Playground
    # You don't need to provide Playground if you don't want to
    # but keep on mind this will not prohibit clients from
    # exploring your API using desktop GraphQL Playground app.
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    # GraphQL queries are always sent as POST
    data = request.get_json()

    # Note: Passing the request to the context is optional.
    # In Flask, the current request is always accessible as flask.request
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(debug=True)
