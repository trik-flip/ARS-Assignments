from organism import Organism


class Species:
    leader: Organism
    members: list[Organism]
    id: int

    def __init__(self, leader, id) -> None:
        self.leader = leader
        self.id = id
        self.members = []

    def fitness(self) -> float:
        return max([m.fitness() for m in self.members])

    def add_member(self, member: Organism):
        self.members.append(member)
        member.species_id = self.id
        if member.fitness() > self.leader.fitness():
            self.leader = member

    def remove_member(self, member: Organism):
        self.members.remove(member)

    def speciation_difference(self, member: Organism):
        return sum(m.speciation_difference(member) for m in self.members)
