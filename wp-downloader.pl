#!/usr/bin/perl

=head
Идем по всему файлу
Ищем урл
Если домен в списке
  Скачиваем и кладем в нужную папку
  Заменяем урл
Иначе
  Просто показываем что есть такой нескаченный урл

Проходим по всему файлу еще раз
Ищем артефакты
  Домены

=cut

use strict;
use warnings;
use Term::ANSIColor;

# Список допустимых доменов
my @domains = ("promo.findoil.ru", "elit-stones.ru");

my $file = join '', <STDIN>;

sub download_and_replace {
	my ($protocol, $domain, $url, $string) = @_;
	if (grep(/^$domain$/, @domains)) {
		my ($location, $args) = split /\?/, $url;
		my ($filename, $dir);
		if ($location =~ m/^((?:.+\/)?)([^\/]+\.[^\/]+)$/) {
			$dir = $1;
			$filename = $2;
			$dir =~ s/\/$//g;
		}
		if ($filename) {
			# Распознали домен
			printf( "%s/%s/%s%s", $domain, $dir, $filename, $args?"?$args":'');
			if ($dir && !-e $dir) {
				`mkdir -p $dir`;
			}
			my $target = $dir?"$dir/$filename":"$filename";
			unless (-f $target) {
				my $source = "$protocol://$domain/$url".($args?"?$args":"");
				my $curl = `curl -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36" $source --fail --silent --show-error -o $target 2>&1`;
				if ($curl) {
					print colored("Curl error: $curl", 'red on_magenta'), "\n";
				}
				print colored(' Downloaded', 'green'), "\n";
				sleep (3);
			} else {
				print colored(' Exists', 'magenta'), "\n";
			}
		} else {
			print colored("Not file: $string", 'white on_red'), "\n";
			return $string;
		}
		$string =~ s/$domain/{{ host }}\/static\/elit-stones/g;
		return $string;
	} else {
		# Левый домен
		print colored("Unknown domain: $string", 'red on_yellow'), "\n";
		return $string;
	}
}

$file =~ s/["'\s(,](http(?:s)?):\/\/([^\/]+)\/([^"'\s),]+)["'\s),]/download_and_replace($1, $2, $3, $&)/meg;

# Сохраняем измененный файл
open(my $fh, ">", "downloaded-output.html") or die "Can't open < input.txt: $!";
print $fh $file;
close $fh;

exit(0);

for my $domain (@domains) {
	$file =~ s/($domain)/find($1)/meg;
}
