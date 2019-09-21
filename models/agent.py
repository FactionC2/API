from backend.database import db
from models.transport import Transport
from models.module import Module
from models.agent_type import AgentType
from models.agent_task import AgentTask

AgentsTransportsXREF = db.Table('AgentsTransportsXREF',
    db.Column('AgentId', db.Integer, db.ForeignKey('Agent.Id'), primary_key=True),
    db.Column('TransportId', db.Integer, db.ForeignKey('Transport.Id'), primary_key=True)
)

AgentModulesXREF = db.Table('AgentModulesXREF',
    db.Column('AgentId', db.Integer, db.ForeignKey('Agent.Id'), primary_key=True),
    db.Column('ModuleId', db.Integer, db.ForeignKey('Module.Id'), primary_key=True)
)


class Agent(db.Model):
    __tablename__ = "Agent"
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)
    StagingId = db.Column(db.String)
    AesPassword = db.Column(db.String)
    Username = db.Column(db.String)
    Hostname = db.Column(db.String)
    PID = db.Column(db.Integer)
    OperatingSystem = db.Column(db.String)
    Admin = db.Column(db.Boolean)
    AgentTypeId = db.Column(db.Integer, db.ForeignKey('AgentType.Id'), nullable=False)
    StagingResponseId = db.Column(db.Integer, db.ForeignKey('StagingMessage.Id'), nullable=False)
    PayloadId = db.Column(db.Integer, db.ForeignKey('Payload.Id'), nullable=False)
    TransportId = db.Column(db.Integer, db.ForeignKey('Transport.Id'), nullable=False)
    InternalIP = db.Column(db.String)
    ExternalIP = db.Column(db.String)
    InitialCheckin = db.Column(db.DateTime)
    LastCheckin = db.Column(db.DateTime)
    BeaconInterval = db.Column(db.Integer)
    Jitter = db.Column(db.Float)
    Tasks = db.relationship('AgentTask', backref='Agent', lazy=True)
    ConsoleMessages = db.relationship("ConsoleMessage", backref='Agent', lazy=True)
    AvailableTransports = db.relationship('Transport', secondary=AgentsTransportsXREF, lazy='subquery', backref=db.backref('AvailableAgents', lazy=True))
    AvailableModules = db.relationship('Module', secondary=AgentModulesXREF, lazy='subquery', backref=db.backref('AvailableAgents', lazy=True))
    Visible = db.Column(db.Boolean)

    def __repr__(self):
        if self.Name:
            return '<Agent: %s>' % self.Name
        else:
            return '<Agent: %s>' % str(self.Id)



